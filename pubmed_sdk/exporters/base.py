from abc import ABC, abstractmethod
from typing import List, Optional
from ..core.models import ArticleDetails

class BaseExporter(ABC):
    @abstractmethod
    def export(self, data: List[ArticleDetails], filename: str, fields: Optional[List[str]] = None) -> None:
        """Export data to a file.
        
        Args:
            data: List of ArticleDetails to export
            filename: Output filename
            fields: Optional list of fields to include
        """
        pass

    def _validate_data(self, data: List[ArticleDetails], fields: Optional[List[str]] = None) -> List[str]:
        """Validate input data and return fields to export."""
        if not data:
            raise ValueError("Data cannot be empty")
            
        if fields is None:
            return list(data[0].keys())
            
        missing = set(fields) - set(data[0].keys())
        if missing:
            raise ValueError(f"Fields {missing} not found in data")
            
        return fields 