"""CLI Argument Parsing Module

This module handles command-line argument parsing for the API Documentation Finder Agent.
It defines the CLIArguments dataclass and provides the parse_arguments() function.
"""

import argparse
import os
from dataclasses import dataclass

# Load environment variables from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Load SerpAPI key from environment variable
SERPAPI_KEY = os.getenv('SERPAPI_KEY', '')


@dataclass
class CLIArguments:
    """Data class to hold parsed CLI arguments"""
    input_file: str
    output_base: str
    serpapi_key: str


def parse_arguments() -> CLIArguments:
    """
    Parse and validate command-line arguments.
    
    Returns:
        CLIArguments: Parsed arguments with input_file, output_base, and serpapi_key
    
    Raises:
        SystemExit: If required arguments are missing or invalid
    """
    parser = argparse.ArgumentParser(
        description="API Documentation Finder Agent - Automatically find API documentation using OpenAPI search and SerpAPI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --input input.csv
  python main.py --input input.json --output my_results
  python main.py --input data/api_methods.csv --output data/results
        """
    )
    
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input CSV or JSON file containing API methods (required)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='results',
        help='Base name for output files without extension (default: results)'
    )
    
    args = parser.parse_args()
    
    # Validate SerpAPI key is set
    if not SERPAPI_KEY:
        parser.error("SERPAPI_KEY environment variable is not set. Please set it in .env file or environment.")
    
    return CLIArguments(
        input_file=args.input,
        output_base=args.output,
        serpapi_key=SERPAPI_KEY
    )
