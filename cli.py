"""CLI Argument Parsing Module

This module handles command-line argument parsing for the API Documentation Finder Agent.
It defines the CLIArguments dataclass and provides the parse_arguments() function.
"""

import argparse
from dataclasses import dataclass


# Hardcoded SerpAPI key as per requirements
SERPAPI_KEY = "dc2bf39c68168f9a35abdac1b265db678d4e97537344e7dee9848c46e7b43b72"


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
    
    return CLIArguments(
        input_file=args.input,
        output_base=args.output,
        serpapi_key=SERPAPI_KEY
    )
