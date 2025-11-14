"""
Test script for AsyncHTTPClient with 10 API methods.
"""
import asyncio
from http_client import AsyncHTTPClient


async def test_10_methods():
    """Test HTTP client with 10 different API endpoints."""
    
    # 10 test URLs - mix of real APIs
    test_urls = [
        "https://api.github.com/users/github",
        "https://api.github.com/repos/python/cpython",
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/users/1",
        "https://jsonplaceholder.typicode.com/comments/1",
        "https://api.github.com/repos/microsoft/vscode",
        "https://jsonplaceholder.typicode.com/todos/1",
        "https://jsonplaceholder.typicode.com/albums/1",
        "https://api.github.com/repos/nodejs/node",
        "https://jsonplaceholder.typicode.com/photos/1"
    ]
    
    print(f"Testing AsyncHTTPClient with {len(test_urls)} methods...\n")
    
    async with AsyncHTTPClient(max_concurrent=5) as client:
        # Test HEAD requests
        print("=== Testing HEAD requests ===")
        head_tasks = [client.head(url) for url in test_urls]
        head_results = await asyncio.gather(*head_tasks)
        
        for url, status in zip(test_urls, head_results):
            status_text = "✓ OK" if status == 200 else f"✗ {status}"
            print(f"{status_text:8} | {url}")
        
        print(f"\nSuccessful HEAD requests: {sum(1 for s in head_results if s == 200)}/{len(test_urls)}")
        
        # Test GET requests
        print("\n=== Testing GET requests ===")
        get_tasks = [client.get(url) for url in test_urls]
        get_results = await asyncio.gather(*get_tasks)
        
        for url, content in zip(test_urls, get_results):
            if content:
                content_preview = content[:100].replace('\n', ' ')
                print(f"✓ OK     | {url}")
                print(f"         | Preview: {content_preview}...")
            else:
                print(f"✗ FAILED | {url}")
        
        successful_gets = sum(1 for c in get_results if c is not None)
        print(f"\nSuccessful GET requests: {successful_gets}/{len(test_urls)}")
        
        # Summary
        print("\n=== Summary ===")
        print(f"Total endpoints tested: {len(test_urls)}")
        print(f"HEAD success rate: {sum(1 for s in head_results if s == 200)}/{len(test_urls)}")
        print(f"GET success rate: {successful_gets}/{len(test_urls)}")


if __name__ == "__main__":
    asyncio.run(test_10_methods())
