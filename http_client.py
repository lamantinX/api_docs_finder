"""
Async HTTP client wrapper with connection pooling and concurrency control.
"""
import asyncio
from typing import Optional
import aiohttp


class AsyncHTTPClient:
    """
    Asynchronous HTTP client with semaphore-based concurrency control.
    
    Supports context manager protocol for proper resource management.
    Limits concurrent requests to prevent system overload.
    """
    
    def __init__(self, max_concurrent: int = 20):
        """
        Initialize HTTP client with concurrency limit.
        
        Args:
            max_concurrent: Maximum number of concurrent HTTP requests (default: 20)
        """
        self.max_concurrent = max_concurrent
        self.session: Optional[aiohttp.ClientSession] = None
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def __aenter__(self):
        """
        Create aiohttp session with connection pooling.
        
        Returns:
            Self for context manager usage
        """
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Close aiohttp session and cleanup resources.
        
        Args:
            exc_type: Exception type if any
            exc_val: Exception value if any
            exc_tb: Exception traceback if any
        """
        if self.session:
            await self.session.close()
    
    async def head(self, url: str, timeout: int = 10) -> int:
        """
        Perform HEAD request and return status code.
        
        Args:
            url: Target URL
            timeout: Request timeout in seconds (default: 10)
            
        Returns:
            HTTP status code, or -1 on error
        """
        if not self.session:
            raise RuntimeError("HTTP client not initialized. Use 'async with' context manager.")
        
        try:
            async with self.semaphore:
                async with self.session.head(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    return response.status
        except asyncio.TimeoutError:
            # Timeout after 10 seconds - return error code
            return -1
        except aiohttp.ClientError:
            # Network error (connection refused, DNS failure, SSL error, etc.)
            return -1
        except Exception:
            # Any other unexpected error
            return -1
    
    async def get(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Perform GET request with timeout handling.
        
        Args:
            url: Target URL
            timeout: Request timeout in seconds (default: 10)
            
        Returns:
            Response text if successful, None on error
        """
        if not self.session:
            raise RuntimeError("HTTP client not initialized. Use 'async with' context manager.")
        
        try:
            async with self.semaphore:
                async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
                    if response.status == 200:
                        return await response.text()
                    return None
        except asyncio.TimeoutError:
            # Timeout after 10 seconds - return None to indicate error
            return None
        except aiohttp.ClientError:
            # Network error (connection refused, DNS failure, SSL error, etc.)
            return None
        except Exception:
            # Any other unexpected error (parsing, encoding, etc.)
            return None
