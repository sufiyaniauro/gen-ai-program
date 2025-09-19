import csv
import io
from transformers.base_transformer import BaseTransformer

class CSVTransformer(BaseTransformer):
    """Transformer to convert data to CSV format."""
    
    def transform(self, data):
        """Transform data to CSV format.
        
        Args:
            data: Input data (list of dicts, dict, list, or string)
            
        Returns:
            str: CSV formatted string
        """
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            return self._transform_list_of_dicts(data)
        elif isinstance(data, dict):
            return self._transform_list_of_dicts([data])
        elif isinstance(data, list):
            return self._transform_list(data)
        elif isinstance(data, str):
            lines = data.strip().split('\n')
            return self._transform_list(lines)
        else:
            raise ValueError(f"Cannot convert {type(data)} to CSV")
    
    def _transform_list_of_dicts(self, data):
        """Transform a list of dictionaries to CSV."""
        if not data:
            return ""
            
        output = io.StringIO()
        fieldnames = set()
        
        for item in data:
            fieldnames.update(item.keys())
            
        writer = csv.DictWriter(output, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    def _transform_list(self, data):
        """Transform a simple list to CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        for item in data:
            writer.writerow([item])
        return output.getvalue()
