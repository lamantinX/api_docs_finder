"""
Convert API Documentation Finder results to api-tracker format.
"""
import json
import sys


def score_url_specificity(url: str, method_name: str) -> int:
    """
    Score URL based on how specific it is to the method.
    Higher score = more specific.
    
    Args:
        url: URL to score
        method_name: Name of the API method
        
    Returns:
        Specificity score
    """
    score = 0
    url_lower = url.lower()
    method_lower = method_name.lower()
    
    # High bonus for URLs with hashtags (specific sections)
    if '#' in url:
        score += 100
    
    # Bonus for method keywords in URL
    method_words = [w for w in method_lower.split() if len(w) > 3]
    for word in method_words:
        if word in url_lower:
            score += 30
    
    # Penalty for generic patterns
    generic_patterns = [
        '/docs$', '/documentation$', '/api$', '/reference$',
        '/guide$', '/methods/$', '/api/$'
    ]
    for pattern in generic_patterns:
        if url_lower.endswith(pattern.replace('$', '')):
            score -= 50
    
    # Penalty for stackoverflow, medium, community forums
    if any(domain in url_lower for domain in ['stackoverflow.com', 'medium.com', 'community.', 'forum.']):
        score -= 30
    
    # Bonus for official docs domains
    if any(pattern in url_lower for pattern in ['developers.', 'docs.', 'api.', 'dev.']):
        score += 20
    
    # Bonus for specific path depth
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split('/') if p]
    if len(path_parts) >= 4:
        score += 40
    elif len(path_parts) >= 3:
        score += 20
    
    return score


def convert_results(input_file: str, output_file: str):
    """
    Convert results from API Documentation Finder format to api-tracker format.
    
    Args:
        input_file: Path to results JSON from API Documentation Finder
        output_file: Path to output JSON in api-tracker format
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    tracker_format = []
    
    for result in results:
        # Determine which documentation URL to use
        doc_url = None
        doc_type = None
        
        # Priority 1: OpenAPI documentation
        if result.get('openapi_link') and result['openapi_link'] not in ('', 'error'):
            doc_url = result['openapi_link']
            # Determine if it's OpenAPI or HTML based on extension
            if doc_url.endswith(('.json', '.yaml', '.yml')):
                doc_type = 'openapi'
            else:
                doc_type = 'html'
        # Priority 2: Postman collection
        elif result.get('postman_link') and result['postman_link'] not in ('', 'error'):
            doc_url = result['postman_link']
            doc_type = 'postman'
        else:
            # Priority 2: Score all search results and pick the best
            candidates = []
            for field in ['search_method_name', 'search_method_link', 'ai_method_name', 'ai_method_link']:
                url = result.get(field)
                if url and url not in ('', 'error'):
                    score = score_url_specificity(url, result['method'])
                    candidates.append((score, url))
            
            if candidates:
                # Sort by score (highest first) and pick the best
                candidates.sort(reverse=True, key=lambda x: x[0])
                doc_url = candidates[0][1]
                doc_type = 'html'
        
        # Only add if we found documentation
        if doc_url:
            tracker_entry = {
                "url": doc_url,
                "type": doc_type,
                "name": f"{result['name']} API - {result['method']}",
                "description": f"Мониторинг документации метода {result['method']} в {result['name']}"
            }
            
            # Add method_filter for OpenAPI specs
            if doc_type == 'openapi' and result.get('method_link'):
                # Extract path from method_link
                from urllib.parse import urlparse
                parsed = urlparse(result['method_link'])
                if parsed.path:
                    tracker_entry['method_filter'] = parsed.path
            
            tracker_format.append(tracker_entry)
    
    # Save to output file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(tracker_format, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Converted {len(tracker_format)} entries from {len(results)} results")
    print(f"📁 Saved to {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_to_tracker_format.py <input_file> [output_file]")
        print("Example: python convert_to_tracker_format.py test_results.json urls.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "urls.json"
    
    convert_results(input_file, output_file)
