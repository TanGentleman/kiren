import csv

from ..core.models import ArticleDetails
from .base import BaseExporter


class CSVExporter(BaseExporter):
    def export(
        self,
        data: list[ArticleDetails],
        filename: str = "output.csv",
        fields: list[str] | None = None,
    ) -> None:
        fields = self._validate_data(data, fields)
        output_path = self._get_output_path(filename)

        with open(output_path, "w", newline="", encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=fields, extrasaction="ignore")
            dict_writer.writeheader()
            dict_writer.writerows(self._flat_rows(data))
