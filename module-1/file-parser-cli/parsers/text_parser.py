from parsers.base_parser import BaseParser

class TextParser(BaseParser):
    """Parser for plain text files."""
    
    def parse(self, file_path):
        """Parse text file and return content as a string."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Error parsing text file: {str(e)}")
    
    def validate(self, data):
        """Validate text data."""
        if not isinstance(data, str):
            return False, ["Data is not a string"]
        
        errors = []
        if data.strip() == "":
            errors.append("File is empty")
            
        return len(errors) == 0, errors
    
    def filter(self, data, query):
        """Filter text by matching lines."""
        import re
        if not isinstance(data, str):
            return data
        
        lines = data.split('\n')
        matched_lines = [line for line in lines if re.search(query, line)]
        return '\n'.join(matched_lines)
