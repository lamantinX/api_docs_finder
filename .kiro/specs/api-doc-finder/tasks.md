# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create project directory structure with all necessary modules
  - Create requirements.txt with dependencies (aiohttp, tqdm)
  - Create README.md with basic usage instructions
  - _Requirements: 7.1, 7.2_

- [x] 2. Implement input loader for CSV and JSON




  - [x] 2.1 Create loader.py module with InputLoader class and APIMethod dataclass


    - Implement load_from_file() to detect format by extension
    - Implement _load_csv() to parse CSV with columns: name, method, method_link
    - Implement _load_json() to parse JSON array of objects
    - Add validation for required fields (name, method, method_link)
    - Add error handling for missing files and invalid formats
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 3. Implement async HTTP client wrapper






  - [x] 3.1 Create http_client.py module with AsyncHTTPClient class

    - Implement __aenter__ and __aexit__ for context manager support
    - Create aiohttp.ClientSession with connection pooling
    - Implement semaphore-based concurrency control (default 20)
    - Implement async head() method to return status code
    - Implement async get() method with timeout handling (10 seconds)
    - Add proper error handling for network failures
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 8.1, 8.2_

- [x] 4. Implement OpenAPI direct search




  - [x] 4.1 Create openapi_search.py module with OpenAPISearch class


    - Implement _extract_domain() to parse base domain from method_link URL
    - Implement find_openapi() to check standard OpenAPI paths in priority order: /openapi.json, /openapi.yaml, /swagger.json, /swagger.yaml, /api-docs, /redoc
    - Implement _check_path() to perform HEAD request first, then GET if needed
    - Return OpenAPI URL if found (status 200), None otherwise
    - Add async HTTP requests with proper error handling
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 5. Implement SerpAPI multi-search integration




  - [x] 5.1 Create serp_search.py module with SerpAPIMultiSearch class and SearchResults dataclass


    - Implement search_all() to execute all 4 search queries concurrently
    - Implement _search_google_lite() for engine=google_lite queries, extract first organic result link
    - Implement _search_google_ai() for engine=google_ai queries, extract first result link
    - Build query 1: "{name} {method} api documentation link" with google_lite
    - Build query 2: "{name} {method_link} api documentation" with google_lite
    - Build query 3: "{name} {method} api documentation link" with google_ai
    - Build query 4: "{name} {method_link} api documentation" with google_ai
    - Return SearchResults with all 4 fields populated (or "error" if failed)
    - Add error handling for SerpAPI failures and no results
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 6. Implement method processor pipeline



  - [x] 6.1 Create processor.py module with MethodProcessor class and ProcessingResult dataclass


    - Implement process_method() that orchestrates the search pipeline
    - Add OpenAPI direct search as first step
    - If OpenAPI found, populate openapi_link and leave search fields empty
    - If OpenAPI not found, execute all 4 SerpAPI searches and populate search fields
    - Create ProcessingResult with all 8 fields: name, method, method_link, openapi_link, search_method_name, search_method_link, ai_method_name, ai_method_link
    - Add error handling to store "error" in failed fields
    - _Requirements: 2.5, 3.1, 8.4_

- [x] 7. Implement progress logging




  - [x] 7.1 Create logger.py module with ProgressLogger class


    - Initialize tqdm progress bar with total API methods count
    - Implement log_success() to display: ✅ найдено для {name} {method}
    - Implement log_error() to display: ❌ ошибка для {name} {method}: <error>
    - Implement update() to increment progress bar
    - Implement close() to finalize progress bar
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 8. Implement output writer for CSV and JSON




  - [x] 8.1 Create output.py module with OutputWriter class



    - Implement save_results() to save to both CSV and JSON
    - Implement _save_csv() with columns: name, method, method_link, openapi_link, search_method_name, search_method_link, ai_method_name, ai_method_link
    - Implement _save_json() as array of objects with same fields
    - Create {output_base}.csv and {output_base}.json files
    - Add error handling for file write failures
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

- [x] 9. Implement CLI argument parsing




  - [x] 9.1 Create cli.py module with argument parser and CLIArguments dataclass


    - Add --input argument (required) for CSV or JSON file path
    - Add --output argument (optional, default: results) for output base name
    - Hardcode SERPAPI_KEY: dc2bf39c68168f9a35abdac1b265db678d4e97537344e7dee9848c46e7b43b72
    - Implement parse_arguments() function returning CLIArguments
    - Add validation for required arguments and help text
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [x] 10. Implement main orchestrator





  - [x] 10.1 Create main.py module with main() async function


    - Parse CLI arguments using parse_arguments()
    - Load API methods using InputLoader.load_from_file()
    - Initialize AsyncHTTPClient with max_concurrent=20
    - Initialize OpenAPISearch and SerpAPIMultiSearch with hardcoded API key
    - Initialize MethodProcessor with both search components
    - Create ProgressLogger with total methods count
    - Create async tasks for all methods using asyncio.gather()
    - Implement process_with_logging() wrapper for error handling per method
    - Save results using OutputWriter.save_results()
    - Add proper cleanup for all async resources
    - Add entry point with if __name__ == "__main__" and asyncio.run(main())
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 4.1, 4.5, 5.1, 5.5, 6.8, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.1, 8.3, 8.4, 8.5_

- [x] 11. Add comprehensive error handling




  - [x] 11.1 Add error handling across all modules


    - Add try-except blocks for network errors in HTTP client
    - Add timeout error handling (10 seconds) with "error" storage
    - Add SerpAPI error handling to store "error" in failed search fields
    - Add file I/O error handling for input/output operations
    - Ensure all errors are recorded in output files with "error" value
    - Verify that individual method failures don't stop overall processing
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 12. Create example files and documentation





  - [x] 12.1 Use  input files


    - Use input.csv with  API methods and methods links
    - Create example input.json with same data
    - _Requirements: 1.1, 1.2, 1.3_
  

  - [x] 12.2 Update README.md with complete documentation

    - Add installation instructions
    - Add usage examples with CLI arguments
    - Add input format examples (CSV and JSON)
    - Add output format examples (CSV and JSON)
    - Add explanation of OpenAPI priority and SerpAPI fallback
    - Add troubleshooting section
    - _Requirements: 7.5_
