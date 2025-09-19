import json
from transformers.base_transformer import BaseTransformer

class JSONTransformer(BaseTransformer):
    """Transformer to convert data to JSON format."""
    
    def transform(self, data):
        """Transform data to JSON format.
        
        Args:
            data: Input data
            
        Returns:
            str: JSON formatted string
        """
        if isinstance(data, str):
            try:
                parsed_data = json.loads(data)
                return json.dumps(parsed_data, indent=2)
            except json.JSONDecodeError:
                lines = data.strip().split('\n')
                return json.dumps(lines, indent=2)
        else:
            try:
                return json.dumps(data, indent=2)
            except TypeError as e:
                raise ValueError(f"Cannot convert to JSON: {str(e)}")
