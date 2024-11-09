import pandas as pd
from typing import List, Optional
from .base import BaseExporter
from ..core.models import ArticleDetails


class ExcelExporter(BaseExporter):
    def export(self,
               data: List[ArticleDetails],
               filename: str = 'output.xlsx',
               fields: Optional[List[str]] = None) -> None:
        """Export data to Excel file."""
        fields = self._validate_data(data, fields)

        if fields:
            df = pd.DataFrame(data)[fields]
        else:
            df = pd.DataFrame(data)

        df.to_excel(filename, index=False)
