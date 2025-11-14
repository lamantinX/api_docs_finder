"""
OpenAPI direct search module for checking standard OpenAPI/Swagger documentation paths.
"""
from typing import Optional
from urllib.parse import urlparse
from http_client import AsyncHTTPClient
import aiohttp
import asyncio


class OpenAPISearch:
    """
    Search for OpenAPI/Swagger documentation in standard paths.
    
    Checks common OpenAPI documentation paths in priority order to minimize
    the need for expensive search API calls.
    """
    
    STANDARD_PATHS = [
        '/openapi.json',
        '/openapi.yaml',
        '/swagger.json',
        '/swagger.yaml',
        '/api-docs',
        '/redoc'
    ]
    
    def __init__(self, http_client: AsyncHTTPClient):
        """
        Initialize OpenAPI search with HTTP client.
        
        Args:
            http_client: Async HTTP client for making requests
        """
        self.http_client = http_client
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract base domain from method_link URL.
        
        Args:
            url: Full URL of the API method
            
        Returns:
            Base URL with scheme and netloc (e.g., 'https://api.example.com')
        """
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    async def _check_path(self, base_url: str, doc_path: str) -> bool:
        """
        Check if OpenAPI path exists using HEAD request first, then GET if needed.
        
        Args:
            base_url: Base domain URL
            doc_path: OpenAPI documentation path to check
            
        Returns:
            True if path exists (status 200), False otherwise
        """
        full_url = f"{base_url}{doc_path}"
        
        try:
            # Try HEAD request first (faster, less bandwidth)
            status = await self.http_client.head(full_url)
            
            # -1 indicates error (timeout or network failure)
            if status == -1:
                return False
            
            if status == 200:
                return True
            
            # If HEAD not supported (405) or other non-404 error, try GET
            if status != 404:
                response = await self.http_client.get(full_url)
                return response is not None
            
            return False
            
        except Exception:
            # Any unexpected error - path doesn't exist or unreachable
            return False
    
    async def find_openapi(self, method_link: str) -> Optional[str]:
        """
        Search for OpenAPI documentation in standard paths.
        
        Checks standard OpenAPI paths in priority order and returns the first
        valid documentation URL found.
        
        Args:
            method_link: URL of the API method
            
        Returns:
            OpenAPI documentation URL if found, None otherwise
        """
        try:
            base_url = self._extract_domain(method_link)
            
            for doc_path in self.STANDARD_PATHS:
                if await self._check_path(base_url, doc_path):
                    return f"{base_url}{doc_path}"
            
            return None
        except Exception:
            # Error extracting domain or checking paths
            return None

