"""Test search results for a specific API method."""
import asyncio
import aiohttp
from urllib.parse import urlencode
import json


async def test_search(query: str):
    """Test SerpAPI search and show all results."""
    api_key = "dc2bf39c68168f9a35abdac1b265db678d4e97537344e7dee9848c46e7b43b72"
    
    params = {
        'api_key': api_key,
        'engine': 'google',
        'q': query,
        'num': 10
    }
    url = f"https://serpapi.com/search.json?{urlencode(params)}"
    
    print(f"Query: {query}")
    print("=" * 80)
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            if response.status == 200:
                data = json.loads(await response.text())
                organic_results = data.get('organic_results', [])
                
                print(f"\nFound {len(organic_results)} results:\n")
                
                for i, result in enumerate(organic_results, 1):
                    link = result.get('link', 'No link')
                    title = result.get('title', 'No title')
                    snippet = result.get('snippet', 'No snippet')
                    
                    print(f"{i}. {title}")
                    print(f"   URL: {link}")
                    print(f"   Snippet: {snippet[:100]}...")
                    print()


async def main():
    """Test different queries for Zoom Create meeting."""
    queries = [
        "Zoom API Create meeting method documentation",
        "https://api.zoom.us/v2/users/me/meetings api reference documentation",
        "Zoom Create meeting endpoint documentation",
        '"https://api.zoom.us/v2/users/me/meetings" documentation'
    ]
    
    for query in queries:
        await test_search(query)
        print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
