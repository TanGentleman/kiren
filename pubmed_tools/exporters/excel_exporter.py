import pandas as pd

from ..core.models import ArticleDetails
from .base import BaseExporter


class ExcelExporter(BaseExporter):
    def export(
        self,
        data: list[ArticleDetails],
        filename: str = "output.xlsx",
        fields: list[str] | None = None,
    ) -> None:
        """Export data to Excel file."""
        fields = self._validate_data(data, fields)
        output_path = self._get_output_path(filename)

        df = pd.DataFrame(self._flat_rows(data))[fields]

        df.to_excel(output_path, index=False)
