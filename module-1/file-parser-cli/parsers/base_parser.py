from abc import ABC, abstractmethod

class BaseParser(ABC):
    """Abstract base class for all file parsers."""
    
    @abstractmethod
    def parse(self, file_path):
        """Parse the file and return structured data."""
        pass
    
    @abstractmethod
    def validate(self, data):
        """Validate data structure and content.
        
        Returns:
            tuple: (is_valid, error_list)
        """
        pass
    
    def filter(self, data, query):
        """Filter data based on query string.
        
        Args:
            data: The parsed data
            query: String query to filter data
            
        Returns:
            Filtered data
        """
        try:
            import re
            if isinstance(data, list):
                return [item for item in data if self._matches_query(item, query)]
            elif isinstance(data, dict):
                return {k: v for k, v in data.items() if self._matches_query({k: v}, query)}
            else:
                if isinstance(data, str):
                    return "\n".join([line for line in data.split("\n") if re.search(query, line)])
                return data
        except Exception as e:
            raise ValueError(f"Error filtering data: {str(e)}")
    
    def _matches_query(self, item, query):
        """Check if an item matches the query.
        
        Basic implementation for simple string matching.
        """
        import re
        if isinstance(item, dict):
            return any(re.search(query, str(v)) for v in item.values())
        elif isinstance(item, list):
            return any(re.search(query, str(v)) for v in item)
        else:
            return re.search(query, str(item))
