import os
from abc import ABC, abstractmethod
from typing import List, Optional
from ..core.models import ArticleDetails
from ..config import OUTPUT_DIR
from ..parsers.date import convert_publication_date


class BaseExporter(ABC):
    @abstractmethod
    def export(self,
               data: List[ArticleDetails],
               filename: str,
               fields: Optional[List[str]] = None) -> None:
        """Export data to a file.

        Args:
            data: List of ArticleDetails to export
            filename: Output filename
            fields: Optional list of fields to include
        """
        pass

    def _validate_data(self,
                      data: List[ArticleDetails],
                      fields: Optional[List[str]] = None) -> List[str]:
        """Validate input data and return fields to export."""
        if not data:
            raise ValueError("Data cannot be empty")

        if fields is None:
            return list(data[0].keys())

        missing = set(fields) - set(data[0].keys())
        if missing:
            raise ValueError(f"Fields {missing} not found in data")

        return fields

    @staticmethod
    def _flat_rows(data: List[ArticleDetails]) -> List[dict]:
        """Rows for tabular formats: authors joined with '; ', dates as text."""
        rows = []
        for item in data:
            row = dict(item)
            if isinstance(row.get('authors'), list):
                row['authors'] = '; '.join(row['authors'])
            if 'publication_date' in row:
                row['publication_date'] = convert_publication_date(row['publication_date'])
            rows.append(row)
        return rows

    def _get_output_path(self, filename: str) -> str:
        """Full output path for a filename; relative names go under OUTPUT_DIR."""
        path = filename if os.path.isabs(filename) else os.path.join(OUTPUT_DIR, filename)
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        return path
