import json
from parsers.base_parser import BaseParser

class JSONParser(BaseParser):
    """Parser for JSON files."""
    
    def parse(self, file_path):
        """Parse JSON file and return structured data."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error parsing JSON file: {str(e)}")
    
    def validate(self, data):
        """Validate JSON data structure."""
        if data is None:
            return False, ["Data is null"]
        
        errors = []
        if isinstance(data, dict):
            self._validate_dict(data, errors)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, dict):
                    self._validate_dict(item, errors, prefix=f"Item {i}: ")
                    
        return len(errors) == 0, errors
    
    def _validate_dict(self, data, errors, prefix=""):
        """Validate a dictionary recursively."""
        for key, value in data.items():
            if key == "":
                errors.append(f"{prefix}Empty key found")
            if isinstance(value, dict):
                self._validate_dict(value, errors, prefix=f"{prefix}{key}.")
