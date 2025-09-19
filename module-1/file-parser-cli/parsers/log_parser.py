import re
from parsers.base_parser import BaseParser

class LogParser(BaseParser):
    """Parser for log files."""
    
    LOG_PATTERNS = [
        r'(?P<ip>\d+\.\d+\.\d+\.\d+) - (?P<user>.*?) \[(?P<datetime>.*?)\] "(?P<request>.*?)" (?P<status>\d+) (?P<size>\d+)',
        r'(?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(,\d+)?)\s+(?P<level>\w+)\s+(?P<message>.*)'
    ]
    
    def parse(self, file_path):
        """Parse log file and return structured data."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                content = file.read()
                
            lines = content.strip().split('\n')
            
            for pattern in self.LOG_PATTERNS:
                parsed_lines = self._try_parse_with_pattern(lines, pattern)
                if parsed_lines:
                    return parsed_lines
            
            return lines
        except Exception as e:
            raise ValueError(f"Error parsing log file: {str(e)}")
    
    def validate(self, data):
        """Validate log data structure."""
        if not isinstance(data, list):
            return False, ["Data is not a list of log entries"]
        
        errors = []
        if not data:
            errors.append("No log entries found")
            
        return len(errors) == 0, errors
    
    def _try_parse_with_pattern(self, lines, pattern):
        """Try to parse log lines with a specific pattern."""
        compiled_pattern = re.compile(pattern)
        parsed_lines = []
        match_count = 0
        
        for i, line in enumerate(lines[:min(10, len(lines))]):
            match = compiled_pattern.search(line)
            if match:
                match_count += 1
        
        if match_count >= min(10, len(lines)) * 0.7:
            for line in lines:
                match = compiled_pattern.search(line)
                if match:
                    parsed_lines.append(match.groupdict())
                else:
                    parsed_lines.append({"raw": line})
            return parsed_lines
        
        return None
