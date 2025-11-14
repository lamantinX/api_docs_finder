"""Postman collection search module."""

import asyncio
from typing import Optional
from urllib.parse import urlencode, quote

from http_client import AsyncHTTPClient
from loader import APIMethod


class PostmanSearch:
    """Search for Postman collections and workspaces."""
    
    def __init__(self, http_client: AsyncHTTPClient):
        """
        Initialize Postman search.
        
        Args:
            http_client: Async HTTP client for making requests
        """
        self.http_client = http_client
        self.postman_api_base = "https://www.postman.com/search"
    
    async def find_postman_collection(self, api_method: APIMethod) -> Optional[str]:
        """
        Search for Postman collection related to the API method.
        
        Searches Postman public workspace for collections matching the API name.
        
        Args:
            api_method: API method to search for
            
        Returns:
            URL to Postman collection if found, None otherwise
        """
        try:
            # Try multiple search strategies
            results = await asyncio.gather(
                self._search_by_name(api_method.name),
                self._search_by_domain(api_method.method_link),
                return_exceptions=True
            )
            
            # Return first successful result
            for result in results:
                if result and not isinstance(result, Exception) and result != "error":
                    return result
            
            return None
            
        except Exception:
            return None
    
    async def _search_by_name(self, api_name: str) -> Optional[str]:
        """
        Search Postman by API name.
        
        Args:
            api_name: Name of the API service
            
        Returns:
            URL to Postman collection or None
        """
        try:
            # Build search URL for Postman public workspace
            search_query = f"{api_name} API"
            search_url = f"{self.postman_api_base}?q={quote(search_query)}&scope=public&type=collection"
            
            # Make request to Postman search
            response_text = await self.http_client.get(search_url, timeout=10)
            
            if not response_text:
                return None
            
            # Parse HTML response to find collection links
            # Postman collection URLs follow pattern: https://www.postman.com/[workspace]/[collection]
            import re
            
            # Look for collection URLs in the response
            collection_pattern = r'href="(/[^/]+/collection/[^"]+)"'
            matches = re.findall(collection_pattern, response_text)
            
            if matches:
                # Return first collection found
                collection_path = matches[0]
                return f"https://www.postman.com{collection_path}"
            
            return None
            
        except Exception:
            return None
    
    async def _search_by_domain(self, method_link: str) -> Optional[str]:
        """
        Search Postman by API domain.
        
        Args:
            method_link: URL of the API method
            
        Returns:
            URL to Postman collection or None
        """
        try:
            from urllib.parse import urlparse
            
            # Extract domain from method_link
            parsed = urlparse(method_link)
            domain = parsed.netloc
            
            if not domain:
                return None
            
            # Remove common prefixes
            domain_clean = domain.replace('api.', '').replace('www.', '')
            
            # Build search URL
            search_query = domain_clean
            search_url = f"{self.postman_api_base}?q={quote(search_query)}&scope=public&type=collection"
            
            # Make request to Postman search
            response_text = await self.http_client.get(search_url, timeout=10)
            
            if not response_text:
                return None
            
            # Parse HTML response to find collection links
            import re
            
            # Look for collection URLs in the response
            collection_pattern = r'href="(/[^/]+/collection/[^"]+)"'
            matches = re.findall(collection_pattern, response_text)
            
            if matches:
                # Return first collection found
                collection_path = matches[0]
                return f"https://www.postman.com{collection_path}"
            
            return None
            
        except Exception:
            return None
