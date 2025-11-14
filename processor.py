"""Method processor pipeline for orchestrating API documentation search."""

from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse

from loader import APIMethod
from openapi_search import OpenAPISearch
from serp_search import SerpAPIMultiSearch
from postman_search import PostmanSearch


@dataclass
class ProcessingResult:
    """Result of processing a single API method through the search pipeline."""
    name: str
    method: str
    method_link: str
    openapi_link: Optional[str]
    postman_link: Optional[str]
    search_method_name: Optional[str]
    search_method_link: Optional[str]
    ai_method_name: Optional[str]
    ai_method_link: Optional[str]


class MethodProcessor:
    """
    Orchestrates the search pipeline for finding API documentation.
    
    Search priority:
    1. OpenAPI/Swagger direct search
    2. Postman collection search
    3. SerpAPI multi-search fallback
    """
    
    def __init__(
        self,
        openapi_search: OpenAPISearch,
        postman_search: PostmanSearch,
        serp_search: SerpAPIMultiSearch
    ):
        """
        Initialize method processor with search components.
        
        Args:
            openapi_search: OpenAPI direct search component
            postman_search: Postman collection search component
            serp_search: SerpAPI multi-search component
        """
        self.openapi_search = openapi_search
        self.postman_search = postman_search
        self.serp_search = serp_search
    
    @staticmethod
    def _is_valid_url(url: Optional[str]) -> bool:
        """
        Validate if URL has proper format.
        
        Args:
            url: URL string to validate
            
        Returns:
            True if URL is valid (has http/https scheme and domain), False otherwise
        """
        if not url or url == "" or url == "error":
            return False
        
        try:
            parsed = urlparse(url)
            return parsed.scheme in ('http', 'https') and bool(parsed.netloc)
        except Exception:
            return False
    
    async def process_method(self, api_method: APIMethod) -> ProcessingResult:
        """
        Process single API method through search pipeline.
        
        Pipeline:
        1. Try OpenAPI direct search
        2. Try Postman collection search (parallel with OpenAPI)
        3. If neither found, execute all 4 SerpAPI searches
        
        Individual method failures don't stop overall processing - errors are
        recorded as "error" in the corresponding fields.
        
        Args:
            api_method: API method to process
            
        Returns:
            ProcessingResult with all 9 fields populated
        """
        try:
            # Step 1 & 2: Try OpenAPI and Postman searches in parallel
            openapi_link = None
            postman_link = None
            
            try:
                import asyncio
                results = await asyncio.gather(
                    self.openapi_search.find_openapi(api_method.method_link),
                    self.postman_search.find_postman_collection(api_method),
                    return_exceptions=True
                )
                
                openapi_link = results[0] if not isinstance(results[0], Exception) else None
                postman_link = results[1] if not isinstance(results[1], Exception) else None
            except Exception:
                # Both searches failed, continue to SerpAPI
                pass
            
            # If OpenAPI or Postman found, skip SerpAPI search
            if openapi_link or postman_link:
                return ProcessingResult(
                    name=api_method.name,
                    method=api_method.method,
                    method_link=api_method.method_link,
                    openapi_link=openapi_link or "",
                    postman_link=postman_link or "",
                    search_method_name="",
                    search_method_link="",
                    ai_method_name="",
                    ai_method_link=""
                )
            
            # Step 3: Neither OpenAPI nor Postman found - execute all 4 SerpAPI searches
            try:
                search_results = await self.serp_search.search_all(api_method)
                
                return ProcessingResult(
                    name=api_method.name,
                    method=api_method.method,
                    method_link=api_method.method_link,
                    openapi_link="",
                    postman_link="",
                    search_method_name=search_results.search_method_name or "",
                    search_method_link=search_results.search_method_link or "",
                    ai_method_name=search_results.ai_method_name or "",
                    ai_method_link=search_results.ai_method_link or ""
                )
            except Exception:
                # SerpAPI search failed - return with error in search fields
                return ProcessingResult(
                    name=api_method.name,
                    method=api_method.method,
                    method_link=api_method.method_link,
                    openapi_link="",
                    postman_link="",
                    search_method_name="error",
                    search_method_link="error",
                    ai_method_name="error",
                    ai_method_link="error"
                )
            
        except Exception:
            # Complete failure - store "error" in all documentation fields
            return ProcessingResult(
                name=api_method.name,
                method=api_method.method,
                method_link=api_method.method_link,
                openapi_link="error",
                postman_link="error",
                search_method_name="error",
                search_method_link="error",
                ai_method_name="error",
                ai_method_link="error"
            )
