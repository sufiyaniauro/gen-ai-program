from parsers.csv_parser import CSVParser
from parsers.json_parser import JSONParser
from parsers.xml_parser import XMLParser
from parsers.text_parser import TextParser
from parsers.log_parser import LogParser

class ParserFactory:
    """Factory class to create appropriate parser for file format."""
    
    def get_parser(self, file_format):
        """Get the appropriate parser for the specified format.
        
        Args:
            file_format (str): Format of the file (csv, json, xml, txt, log)
            
        Returns:
            BaseParser: Parser instance for the specified format
            
        Raises:
            ValueError: If the format is not supported
        """
        file_format = file_format.lower()
        
        if file_format == "csv":
            return CSVParser()
        elif file_format == "json":
            return JSONParser()
        elif file_format == "xml":
            return XMLParser()
        elif file_format == "txt":
            return TextParser()
        elif file_format == "log":
            return LogParser()
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
