from abc import ABC, abstractmethod

class BaseTransformer(ABC):
    """Abstract base class for data transformers."""
    
    @abstractmethod
    def transform(self, data):
        """Transform data to target format.
        
        Args:
            data: Source data in any format
            
        Returns:
            Data in the target format
        """
        pass
