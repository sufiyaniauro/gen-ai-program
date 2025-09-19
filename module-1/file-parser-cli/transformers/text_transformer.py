import json
from transformers.base_transformer import BaseTransformer

class TextTransformer(BaseTransformer):
    """Transformer to convert data to plain text format."""
    
    def transform(self, data):
        """Transform data to plain text format.
        
        Args:
            data: Input data (dict, list, or string)
            
        Returns:
            str: Plain text string
        """
        if isinstance(data, str):
            return data
        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data):
                lines = []
                for item in data:
                    lines.append(str(item))
                return '\n'.join(lines)
            else:
                return '\n'.join(str(item) for item in data)
        elif isinstance(data, dict):
            try:
                return json.dumps(data, indent=2)
            except:
                return str(data)
        else:
            return str(data)
