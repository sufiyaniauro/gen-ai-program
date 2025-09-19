from transformers.base_transformer import BaseTransformer
from transformers.csv_transformer import CSVTransformer
from transformers.json_transformer import JSONTransformer
from transformers.xml_transformer import XMLTransformer
from transformers.text_transformer import TextTransformer

class TransformerFactory:
    """Factory class to create appropriate transformer based on source and target formats."""
    
    def get_transformer(self, source_format, target_format):
        """Get a transformer to convert from source format to target format.
        
        Args:
            source_format (str): Source file format
            target_format (str): Target file format
            
        Returns:
            BaseTransformer: Appropriate transformer
            
        Raises:
            ValueError: If the transformation is not supported
        """
        source_format = source_format.lower()
        target_format = target_format.lower()
        
        if target_format == "csv":
            return CSVTransformer()
        elif target_format == "json":
            return JSONTransformer()
        elif target_format == "xml":
            return XMLTransformer()
        elif target_format == "txt":
            return TextTransformer()
        else:
            raise ValueError(f"Unsupported target format: {target_format}")
