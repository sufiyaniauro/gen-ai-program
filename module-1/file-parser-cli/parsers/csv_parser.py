import csv
from parsers.base_parser import BaseParser

class CSVParser(BaseParser):
    """Parser for CSV files."""
    
    def parse(self, file_path):
        """Parse CSV file and return list of dictionaries."""
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                return list(reader)
        except Exception as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")
    
    def validate(self, data):
        """Validate CSV data structure."""
        if not isinstance(data, list):
            return False, ["Data is not a list of records"]
        
        errors = []
        if not data:
            return True, []  
            
        if len(data) > 1:
            fields = set(data[0].keys())
            for i, row in enumerate(data[1:], 2):
                row_fields = set(row.keys())
                if fields != row_fields:
                    errors.append(f"Row {i} has different fields than the header")
                    
        for i, row in enumerate(data, 1):
            for field, value in row.items():
                if value == "":
                    errors.append(f"Empty value in row {i}, field '{field}'")
        
        return len(errors) == 0, errors
