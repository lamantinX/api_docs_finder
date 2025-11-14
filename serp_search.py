"""SerpAPI multi-search integration module."""

import asyncio
from dataclasses import dataclass
from typing import Optional, List
from urllib.parse import urlencode, urlparse

from http_client import AsyncHTTPClient
from loader import APIMethod


@dataclass
class SearchResults:
    """Results from all 4 SerpAPI search queries."""
    search_method_name: Optional[str]      # google_light: "{name} {method} api documentation link"
    search_method_link: Optional[str]      # google_light: "{name} {method_link} api documentation"
    ai_method_name: Optional[str]          # google_ai_mode: "{name} {method} api documentation link"
    ai_method_link: Optional[str]          # google_ai_mode: "{name} {method_link} api documentation"


class SerpAPIMultiSearch:
    """Execute multiple SerpAPI searches with different engines and queries."""
    
    def __init__(self, api_key: str, http_client: AsyncHTTPClient):
        """
        Initialize SerpAPI multi-search.
        
        Args:
            api_key: SerpAPI authentication key
            http_client: Async HTTP client for making requests
        """
        self.api_key = api_key
        self.http_client = http_client
        self.base_url = "https://serpapi.com/search.json"
    
    def _is_relevant_to_service(self, url: str, title: str, snippet: str, api_method: APIMethod) -> bool:
        """
        Check if URL is relevant to the API service.
        
        Args:
            url: URL to check
            title: Page title
            snippet: Page snippet/description
            api_method: API method being searched
            
        Returns:
            True if URL is relevant to the service, False otherwise
        """
        url_lower = url.lower()
        title_lower = title.lower() if title else ""
        snippet_lower = snippet.lower() if snippet else ""
        name_lower = api_method.name.lower()
        
        # Extract domain from method_link for comparison
        try:
            method_domain = urlparse(api_method.method_link).netloc.lower()
            # Remove common prefixes
            method_domain_clean = method_domain.replace('api.', '').replace('www.', '')
        except:
            method_domain = ""
            method_domain_clean = ""
        
        # Check 1: URL domain matches or contains service name
        url_domain = urlparse(url).netloc.lower()
        url_domain_clean = url_domain.replace('api.', '').replace('www.', '').replace('docs.', '').replace('developers.', '').replace('dev.', '')
        
        # Direct domain match (e.g., slack.com matches api.slack.com)
        if method_domain_clean and method_domain_clean in url_domain_clean:
            return True
        
        # Service name in domain (e.g., "hubspot" in "developers.hubspot.com")
        name_parts = name_lower.split()
        for part in name_parts:
            if len(part) > 3 and part in url_domain_clean:
                return True
        
        # Check 2: Service name in title or snippet
        combined_text = f"{title_lower} {snippet_lower}"
        
        # Service name appears in title/snippet
        if name_lower in combined_text:
            return True
        
        # Check for common variations (e.g., "Slack API" for "Slack")
        for part in name_parts:
            if len(part) > 3 and part in combined_text:
                return True
        
        # Check 3: Known documentation domains (official docs sites)
        official_doc_domains = [
            'docs.', 'developers.', 'dev.', 'api.', 'developer.',
            'learn.microsoft.com', 'github.com', 'postman.com'
        ]
        
        # If it's an official doc domain and mentions the service, it's likely relevant
        if any(domain in url_domain for domain in official_doc_domains):
            if name_lower in combined_text or any(part in combined_text for part in name_parts if len(part) > 3):
                return True
        
        # If none of the checks passed, URL is not relevant
        return False
    
    def _score_url_relevance(self, url: str, api_method: APIMethod) -> int:
        """
        Score URL relevance based on specificity indicators.
        Higher score = more specific documentation link.
        
        Args:
            url: URL to score
            api_method: API method being searched
            
        Returns:
            Relevance score (higher is better)
        """
        score = 0
        url_lower = url.lower()
        method_lower = api_method.method.lower()
        name_lower = api_method.name.lower()
        
        # Extract domain from method_link
        try:
            method_domain = urlparse(api_method.method_link).netloc.lower()
            method_domain_clean = method_domain.replace('api.', '').replace('www.', '')
        except:
            method_domain_clean = ""
        
        url_domain = urlparse(url).netloc.lower()
        url_domain_clean = url_domain.replace('api.', '').replace('www.', '').replace('docs.', '').replace('developers.', '').replace('dev.', '')
        
        # High bonus for matching domain
        if method_domain_clean and method_domain_clean in url_domain_clean:
            score += 100
        
        # Bonus for service name in domain
        name_parts = name_lower.split()
        for part in name_parts:
            if len(part) > 3 and part in url_domain_clean:
                score += 80
        
        # Bonus for URLs with hashtags (usually point to specific sections)
        if '#' in url:
            score += 50
        
        # Bonus for URLs containing method keywords
        method_words = method_lower.split()
        for word in method_words:
            if len(word) > 3 and word in url_lower:
                score += 20
        
        # Bonus for URLs with specific paths (not just root or /docs)
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split('/') if p]
        if len(path_parts) >= 3:  # e.g., /api/meetings/create
            score += 30
        elif len(path_parts) >= 2:
            score += 15
        
        # Penalty for generic documentation pages
        generic_patterns = ['/docs', '/documentation', '/api', '/reference']
        if any(pattern in url_lower and url_lower.endswith(pattern) for pattern in generic_patterns):
            score -= 20
        
        # Bonus for "methods", "endpoints", "operations" in URL
        if any(keyword in url_lower for keyword in ['method', 'endpoint', 'operation', 'post/', 'get/', 'put/', 'delete/']):
            score += 25
        
        return score
    
    def _select_best_result(self, results: List[dict], api_method: APIMethod) -> Optional[str]:
        """
        Select the most relevant result from search results.
        
        Filters results to only include those relevant to the API service,
        then scores and returns the best match.
        
        Args:
            results: List of organic search results
            api_method: API method being searched
            
        Returns:
            Best matching URL or None
        """
        if not results:
            return None
        
        # First, filter results to only relevant ones
        relevant_results = []
        for result in results[:10]:  # Check top 10 results
            link = result.get('link')
            title = result.get('title', '')
            snippet = result.get('snippet', '')
            
            if link and self._is_relevant_to_service(link, title, snippet, api_method):
                relevant_results.append(result)
        
        if not relevant_results:
            # No relevant results found, return None (will be marked as "error")
            return None
        
        # Score all relevant results
        scored_results = []
        for result in relevant_results[:5]:  # Score top 5 relevant results
            link = result.get('link')
            if link:
                score = self._score_url_relevance(link, api_method)
                scored_results.append((score, link))
        
        if not scored_results:
            return None
        
        # Return highest scoring result
        scored_results.sort(reverse=True, key=lambda x: x[0])
        return scored_results[0][1]
    
    async def search_all(self, api_method: APIMethod) -> SearchResults:
        """
        Execute all 4 search queries concurrently and return results.
        
        Query pattern for each engine:
        - Query 1 (google_light): "{name} {method} api documentation link"
        - Query 2 (google_light): "{name} {method_link} api documentation"
        - Query 3 (google_ai_mode): "{name} {method} api documentation link"
        - Query 4 (google_ai_mode): "{name} {method_link} api documentation"
        
        Args:
            api_method: API method to search documentation for
            
        Returns:
            SearchResults with all 4 fields populated (or "error" if failed)
        """
        try:
            # Build queries according to specification
            # Query 1: google_light with name + method
            query1 = f"{api_method.name} {api_method.method} api documentation link"
            # Query 2: google_light with name + method_link
            query2 = f"{api_method.name} {api_method.method_link} api documentation"
            # Query 3: google_ai_mode with name + method
            query3 = f"{api_method.name} {api_method.method} api documentation link"
            # Query 4: google_ai_mode with name + method_link
            query4 = f"{api_method.name} {api_method.method_link} api documentation"
            
            # Execute all 4 searches concurrently with exception handling
            results = await asyncio.gather(
                self._search_google_light(query1, api_method),
                self._search_google_light(query2, api_method),
                self._search_google_ai_mode(query3, api_method),
                self._search_google_ai_mode(query4, api_method),
                return_exceptions=True
            )
            
            # Extract results, converting exceptions to "error"
            search_method_name = results[0] if not isinstance(results[0], Exception) else "error"
            search_method_link = results[1] if not isinstance(results[1], Exception) else "error"
            ai_method_name = results[2] if not isinstance(results[2], Exception) else "error"
            ai_method_link = results[3] if not isinstance(results[3], Exception) else "error"
            
            return SearchResults(
                search_method_name=search_method_name,
                search_method_link=search_method_link,
                ai_method_name=ai_method_name,
                ai_method_link=ai_method_link
            )
        except Exception:
            # If entire search_all fails, return all errors
            return SearchResults(
                search_method_name="error",
                search_method_link="error",
                ai_method_name="error",
                ai_method_link="error"
            )

    async def _search_google_light(self, query: str, api_method: APIMethod) -> Optional[str]:
        """
        Execute google_light search and extract best matching result link.
        
        google_light is a lightweight version of Google Search API.
        
        Args:
            query: Search query string
            api_method: API method being searched (for relevance scoring)
            
        Returns:
            Best matching result link or "error" if failed/no results
        """
        try:
            # Build SerpAPI request URL with google_light engine
            params = {
                'api_key': self.api_key,
                'engine': 'google_light',
                'q': query
            }
            url = f"{self.base_url}?{urlencode(params)}"
            
            # Make async GET request with timeout handling
            response_text = await self.http_client.get(url, timeout=10)
            
            if not response_text:
                # Timeout or network error occurred
                return "error"
            
            # Parse JSON response
            import json
            response_data = json.loads(response_text)
            
            # Check for SerpAPI error response
            if 'error' in response_data:
                return "error"
            
            # Extract organic results and select best match
            organic_results = response_data.get('organic_results', [])
            best_link = self._select_best_result(organic_results, api_method)
            
            if best_link:
                return best_link
            
            # No results found
            return "error"
            
        except json.JSONDecodeError:
            # Invalid JSON response from SerpAPI
            return "error"
        except asyncio.TimeoutError:
            # Request timeout
            return "error"
        except Exception:
            # Any other error (network, parsing, etc.)
            return "error"
    
    async def _search_google_ai_mode(self, query: str, api_method: APIMethod) -> Optional[str]:
        """
        Execute google_ai_mode search and extract best matching result link.
        
        google_ai_mode uses AI-powered search with different response structure.
        Returns references instead of organic_results.
        
        Args:
            query: Search query string
            api_method: API method being searched (for relevance scoring)
            
        Returns:
            Best matching result link or "error" if failed/no results
        """
        try:
            # Build SerpAPI request URL with google_ai_mode engine
            params = {
                'api_key': self.api_key,
                'engine': 'google_ai_mode',
                'q': query
            }
            url = f"{self.base_url}?{urlencode(params)}"
            
            # Make async GET request with timeout handling
            response_text = await self.http_client.get(url, timeout=10)
            
            if not response_text:
                # Timeout or network error occurred
                return "error"
            
            # Parse JSON response
            import json
            response_data = json.loads(response_text)
            
            # Check for SerpAPI error response
            if 'error' in response_data:
                return "error"
            
            # google_ai_mode returns 'references' instead of 'organic_results'
            references = response_data.get('references', [])
            
            if not references:
                return "error"
            
            # Convert references to format compatible with _select_best_result
            # References have 'link' and 'title' fields
            formatted_results = []
            for ref in references:
                if 'link' in ref:
                    formatted_results.append({
                        'link': ref['link'],
                        'title': ref.get('title', ''),
                        'snippet': ref.get('snippet', '')
                    })
            
            best_link = self._select_best_result(formatted_results, api_method)
            
            if best_link:
                return best_link
            
            # No results found
            return "error"
            
        except json.JSONDecodeError:
            # Invalid JSON response from SerpAPI
            return "error"
        except asyncio.TimeoutError:
            # Request timeout
            return "error"
        except Exception:
            # Any other error (network, parsing, etc.)
            return "error"
