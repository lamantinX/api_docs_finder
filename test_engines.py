"""Test different SerpAPI engines."""
import asyncio
import aiohttp
from urllib.parse import urlencode
import json


async def test_engine(engine: str, query: str):
    """Test a specific SerpAPI engine."""
    api_key = "dc2bf39c68168f9a35abdac1b265db678d4e97537344e7dee9848c46e7b43b72"
    
    params = {
        'api_key': api_key,
        'engine': engine,
        'q': query
    }
    url = f"https://serpapi.com/search.json?{urlencode(params)}"
    
    print(f"\n{'='*80}")
    print(f"Testing engine: {engine}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as response:
                print(f"Status: {response.status}")
                text = await response.text()
                
                if response.status == 200:
                    data = json.loads(text)
                    
                    if 'error' in data:
                        print(f"❌ API Error: {data['error']}")
                    else:
                        print(f"✅ Success!")
                        print(f"Response keys: {list(data.keys())}")
                        
                        if 'organic_results' in data:
                            results = data['organic_results']
                            print(f"Found {len(results)} organic results")
                            if results:
                                print(f"\nFirst result:")
                                print(f"  Title: {results[0].get('title', 'N/A')}")
                                print(f"  Link: {results[0].get('link', 'N/A')}")
                        
                        if 'ai_overview' in data:
                            print(f"AI Overview present: {bool(data['ai_overview'])}")
                else:
                    print(f"❌ HTTP Error: {response.status}")
                    print(f"Response: {text[:500]}")
                    
        except asyncio.TimeoutError:
            print("❌ Request timeout")
        except Exception as e:
            print(f"❌ Error: {e}")


async def main():
    """Test both engines."""
    query = "Slack Send message api documentation"
    
    # Test google_light
    await test_engine('google_light', query)
    
    # Test google_ai_mode
    await test_engine('google_ai_mode', query)
    
    # Test regular google
    await test_engine('google', query)


if __name__ == "__main__":
    asyncio.run(main())
