"""
Main orchestrator for API Documentation Finder Agent.

This module coordinates all components to process API methods and find their documentation
through OpenAPI direct search and SerpAPI multi-search fallback.
"""

import asyncio
import os
import sys
from typing import List

# Load environment variables from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from cli import parse_arguments
from loader import InputLoader, APIMethod
from http_client import AsyncHTTPClient
from openapi_search import OpenAPISearch
from postman_search import PostmanSearch
from serp_search import SerpAPIMultiSearch
from processor import MethodProcessor, ProcessingResult
from logger import ProgressLogger
from output import OutputWriter


async def process_with_logging(
    processor: MethodProcessor,
    api_method: APIMethod,
    logger: ProgressLogger
) -> ProcessingResult:
    """
    Process API method and log result with proper error handling.
    
    Individual method failures don't stop overall processing - errors are
    caught and recorded as "error" in the output fields.
    
    Args:
        processor: Method processor instance
        api_method: API method to process
        logger: Progress logger instance
        
    Returns:
        ProcessingResult with all fields populated or "error" on failure
    """
    try:
        result = await processor.process_method(api_method)
        
        # Check if result has any successful findings
        has_success = (
            (result.openapi_link and result.openapi_link != "error") or
            (result.postman_link and result.postman_link != "error") or
            (result.search_method_name and result.search_method_name not in ("", "error")) or
            (result.search_method_link and result.search_method_link not in ("", "error")) or
            (result.ai_method_name and result.ai_method_name not in ("", "error")) or
            (result.ai_method_link and result.ai_method_link not in ("", "error"))
        )
        
        if has_success:
            logger.log_success(api_method.name, api_method.method)
        else:
            logger.log_error(api_method.name, api_method.method, "No documentation found")
        
        return result
    except asyncio.TimeoutError:
        # Timeout error - record as error
        logger.log_error(api_method.name, api_method.method, "Timeout after 10 seconds")
        return ProcessingResult(
            name=api_method.name,
            method=api_method.method,
            method_link=api_method.method_link,
            openapi_link="error",
            postman_link="error",
            search_method_name="error",
            search_method_link="error",
            ai_method_name="error",
            ai_method_link="error"
        )
    except Exception as e:
        # Any other error - record as error
        logger.log_error(api_method.name, api_method.method, str(e))
        return ProcessingResult(
            name=api_method.name,
            method=api_method.method,
            method_link=api_method.method_link,
            openapi_link="error",
            postman_link="error",
            search_method_name="error",
            search_method_link="error",
            ai_method_name="error",
            ai_method_link="error"
        )
    finally:
        # Always update progress bar, even on error
        logger.update()


async def main():
    """
    Main entry point for API Documentation Finder Agent.
    
    Orchestrates the complete pipeline:
    1. Parse CLI arguments
    2. Load API methods from input file
    3. Initialize all components
    4. Process methods concurrently
    5. Save results to CSV and JSON
    
    Individual method failures don't stop overall processing - all errors
    are caught and recorded in the output files.
    """
    try:
        # Step 1: Parse CLI arguments with error handling
        try:
            args = parse_arguments()
        except SystemExit:
            # argparse calls sys.exit on error, let it propagate
            raise
        except Exception as e:
            print(f"Error parsing arguments: {e}")
            sys.exit(1)
        
        # Step 2: Load API methods from input file with error handling
        try:
            api_methods = InputLoader.load_from_file(args.input_file)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except ValueError as e:
            print(f"Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading input file: {e}")
            sys.exit(1)
        
        if not api_methods:
            print("Error: No valid API methods found in input file")
            sys.exit(1)
        
        print(f"Loaded {len(api_methods)} API methods from {args.input_file}")
        
        # Step 3: Initialize components with async HTTP client
        try:
            async with AsyncHTTPClient(max_concurrent=20) as http_client:
                # Initialize search components
                openapi_search = OpenAPISearch(http_client)
                postman_search = PostmanSearch(http_client)
                serp_search = SerpAPIMultiSearch(args.serpapi_key, http_client)
                processor = MethodProcessor(openapi_search, postman_search, serp_search)
                
                # Step 4: Create progress logger
                logger = ProgressLogger(len(api_methods))
                
                # Step 5: Create async tasks for all methods
                # Each task has its own error handling to prevent one failure from stopping others
                tasks = [
                    process_with_logging(processor, method, logger)
                    for method in api_methods
                ]
                
                # Execute all tasks concurrently with return_exceptions=False
                # (errors are already handled in process_with_logging)
                results: List[ProcessingResult] = await asyncio.gather(*tasks)
                
                # Step 6: Close progress logger
                logger.close()
                
                # Step 7: Save results to CSV and JSON with error handling
                try:
                    OutputWriter.save_results(results, args.output_base)
                    print(f"\n✅ Results saved to {args.output_base}.csv and {args.output_base}.json")
                except IOError as e:
                    print(f"\nError saving results: {e}")
                    sys.exit(1)
                except Exception as e:
                    print(f"\nUnexpected error saving results: {e}")
                    sys.exit(1)
        
        except Exception as e:
            print(f"\nError during processing: {e}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        sys.exit(130)
    except SystemExit:
        # Re-raise SystemExit to preserve exit codes
        raise
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
