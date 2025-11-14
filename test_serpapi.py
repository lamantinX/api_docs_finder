"""Test SerpAPI connection and quota."""
import asyncio
import aiohttp
from urllib.parse import urlencode


async def test_serpapi():
    """Test SerpAPI with a simple query."""
    api_key = "dc2bf39c68168f9a35abdac1b265db678d4e97537344e7dee9848c46e7b43b72"
    
    # Test query
    params = {
        'api_key': api_key,
        'engine': 'google',
        'q': 'Slack Send message api documentation link'
    }
    url = f"https://serpapi.com/search.json?{urlencode(params)}"
    
    print(f"Testing SerpAPI...")
    print(f"Query: {params['q']}")
    print(f"Engine: {params['engine']}")
    print()
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                print(f"Status: {response.status}")
                text = await response.text()
                print(f"Response length: {len(text)} bytes")
                print()
                print("Response preview:")
                print(text[:500])
                print()
                
                if response.status == 200:
                    import json
                    data = json.loads(text)
                    
                    if 'error' in data:
                        print(f"❌ SerpAPI Error: {data['error']}")
                    elif 'organic_results' in data:
                        print(f"✅ Found {len(data['organic_results'])} organic results")
                        if data['organic_results']:
                            first = data['organic_results'][0]
                            print(f"First result: {first.get('link', 'No link')}")
                    else:
                        print("⚠️ Unexpected response structure")
                        print(f"Keys: {list(data.keys())}")
                else:
                    print(f"❌ HTTP Error: {response.status}")
        except asyncio.TimeoutError:
            print("❌ Request timeout")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_serpapi())
