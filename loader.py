"""Input loader for CSV and JSON files containing API methods."""

import csv
import json
import os
from dataclasses import dataclass
from typing import List


@dataclass
class APIMethod:
    """Represents an API method with its metadata."""
    name: str
    method: str
    method_link: str


class InputLoader:
    """Loads API methods from CSV or JSON files."""
    
    @staticmethod
    def load_from_file(file_path: str) -> List[APIMethod]:
        """
        Load API methods from CSV or JSON file.
        Detects format by file extension.
        
        Args:
            file_path: Path to the input file (.csv or .json)
            
        Returns:
            List of APIMethod objects
            
        Raises:
            FileNotFoundError: If the input file does not exist
            ValueError: If the file format is invalid or unsupported
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.csv':
            return InputLoader._load_csv(file_path)
        elif file_extension == '.json':
            return InputLoader._load_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Only .csv and .json are supported.")
    
    @staticmethod
    def _load_csv(file_path: str) -> List[APIMethod]:
        """
        Parse CSV file with columns: name, method, method_link.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            List of APIMethod objects
            
        Raises:
            ValueError: If CSV format is invalid or required fields are missing
        """
        api_methods = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate that required columns exist
                if reader.fieldnames is None:
                    raise ValueError("CSV file is empty or has no header")
                
                required_fields = {'name', 'method', 'method_link'}
                missing_fields = required_fields - set(reader.fieldnames)
                if missing_fields:
                    raise ValueError(f"CSV file missing required columns: {missing_fields}")
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    # Validate that all required fields are present and non-empty
                    missing_values = [field for field in required_fields if not row.get(field, '').strip()]
                    
                    if missing_values:
                        print(f"Warning: Skipping row {row_num} - missing required fields: {missing_values}")
                        continue
                    
                    api_methods.append(APIMethod(
                        name=row['name'].strip(),
                        method=row['method'].strip(),
                        method_link=row['method_link'].strip()
                    ))
        
        except csv.Error as e:
            raise ValueError(f"Error parsing CSV file: {e}")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
            raise ValueError(f"Error reading CSV file: {e}")
        
        return api_methods
    
    @staticmethod
    def _load_json(file_path: str) -> List[APIMethod]:
        """
        Parse JSON file as an array of objects with fields: name, method, method_link.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            List of APIMethod objects
            
        Raises:
            ValueError: If JSON format is invalid or required fields are missing
        """
        api_methods = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise ValueError("JSON file must contain an array of objects")
            
            required_fields = {'name', 'method', 'method_link'}
            
            for index, item in enumerate(data):
                if not isinstance(item, dict):
                    print(f"Warning: Skipping item {index} - not a valid object")
                    continue
                
                # Validate that all required fields are present and non-empty
                missing_fields = [field for field in required_fields if not item.get(field, '')]
                
                if missing_fields:
                    print(f"Warning: Skipping item {index} - missing required fields: {missing_fields}")
                    continue
                
                api_methods.append(APIMethod(
                    name=str(item['name']).strip(),
                    method=str(item['method']).strip(),
                    method_link=str(item['method_link']).strip()
                ))
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Error parsing JSON file: {e}")
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise
            raise ValueError(f"Error reading JSON file: {e}")
        
        return api_methods
