"""Output writer for saving processing results to CSV and JSON formats."""

import csv
import json
from typing import List, Optional
from pathlib import Path
from urllib.parse import urlparse

from processor import ProcessingResult


class OutputWriter:
    """
    Handles saving processing results to both CSV and JSON formats.
    
    Creates two output files:
    - {output_base}.csv with all result fields
    - {output_base}.json as array of objects
    """
    
    @staticmethod
    def _validate_url(url: Optional[str]) -> str:
        """
        Validate URL format and return cleaned value.
        
        Returns:
            - Original URL if valid
            - Empty string if None or empty
            - "error" if URL format is invalid
        
        Args:
            url: URL string to validate
        """
        if not url or url == "":
            return ""
        
        if url == "error":
            return "error"
        
        try:
            parsed = urlparse(url)
            # Check if URL has scheme and netloc (domain)
            if parsed.scheme in ('http', 'https') and parsed.netloc:
                return url
            else:
                return "error"
        except Exception:
            return "error"
    
    @staticmethod
    def save_results(results: List[ProcessingResult], output_base: str):
        """
        Save results to both CSV and JSON files.
        
        Creates {output_base}.csv and {output_base}.json files with all
        processing results including OpenAPI links and search results.
        
        Args:
            results: List of processing results to save
            output_base: Base name for output files (without extension)
            
        Raises:
            IOError: If files cannot be written
        """
        try:
            csv_path = f"{output_base}.csv"
            json_path = f"{output_base}.json"
            
            # Save CSV with error handling
            try:
                OutputWriter._save_csv(results, csv_path)
            except Exception as e:
                raise IOError(f"Failed to write CSV file: {str(e)}")
            
            # Save JSON with error handling
            try:
                OutputWriter._save_json(results, json_path)
            except Exception as e:
                raise IOError(f"Failed to write JSON file: {str(e)}")
            
        except IOError:
            # Re-raise IOError as-is
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise IOError(f"Failed to write output files: {str(e)}")
    
    @staticmethod
    def _save_csv(results: List[ProcessingResult], file_path: str):
        """
        Save results to CSV file with proper column order.
        
        Columns: name, method, method_link, openapi_link, search_method_name,
                 search_method_link, ai_method_name, ai_method_link
        
        Args:
            results: List of processing results
            file_path: Path to CSV file
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'name',
                    'method',
                    'method_link',
                    'openapi_link',
                    'postman_link',
                    'search_method_name',
                    'search_method_link',
                    'ai_method_name',
                    'ai_method_link'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    writer.writerow({
                        'name': result.name,
                        'method': result.method,
                        'method_link': OutputWriter._validate_url(result.method_link),
                        'openapi_link': OutputWriter._validate_url(result.openapi_link),
                        'postman_link': OutputWriter._validate_url(result.postman_link),
                        'search_method_name': OutputWriter._validate_url(result.search_method_name),
                        'search_method_link': OutputWriter._validate_url(result.search_method_link),
                        'ai_method_name': OutputWriter._validate_url(result.ai_method_name),
                        'ai_method_link': OutputWriter._validate_url(result.ai_method_link)
                    })
        
        except PermissionError as e:
            raise IOError(f"Permission denied writing to {file_path}: {str(e)}")
        except OSError as e:
            raise IOError(f"OS error writing CSV file {file_path}: {str(e)}")
        except csv.Error as e:
            raise IOError(f"CSV formatting error in {file_path}: {str(e)}")
        except Exception as e:
            raise IOError(f"Failed to write CSV file {file_path}: {str(e)}")
    
    @staticmethod
    def _save_json(results: List[ProcessingResult], file_path: str):
        """
        Save results to JSON file as array of objects.
        
        Each object contains all 8 fields from ProcessingResult.
        
        Args:
            results: List of processing results
            file_path: Path to JSON file
            
        Raises:
            IOError: If file cannot be written
        """
        try:
            output_data = []
            
            for result in results:
                output_data.append({
                    'name': result.name,
                    'method': result.method,
                    'method_link': OutputWriter._validate_url(result.method_link),
                    'openapi_link': OutputWriter._validate_url(result.openapi_link),
                    'postman_link': OutputWriter._validate_url(result.postman_link),
                    'search_method_name': OutputWriter._validate_url(result.search_method_name),
                    'search_method_link': OutputWriter._validate_url(result.search_method_link),
                    'ai_method_name': OutputWriter._validate_url(result.ai_method_name),
                    'ai_method_link': OutputWriter._validate_url(result.ai_method_link)
                })
            
            with open(file_path, 'w', encoding='utf-8') as jsonfile:
                json.dump(output_data, jsonfile, indent=2, ensure_ascii=False)
        
        except PermissionError as e:
            raise IOError(f"Permission denied writing to {file_path}: {str(e)}")
        except OSError as e:
            raise IOError(f"OS error writing JSON file {file_path}: {str(e)}")
        except json.JSONEncodeError as e:
            raise IOError(f"JSON encoding error in {file_path}: {str(e)}")
        except Exception as e:
            raise IOError(f"Failed to write JSON file {file_path}: {str(e)}")
