import csv
from typing import List, Optional
from .base import BaseExporter
from ..core.models import ArticleDetails


class CSVExporter(BaseExporter):
    def export(self,
               data: List[ArticleDetails],
               filename: str = 'output.csv',
               fields: Optional[List[str]] = None) -> None:
        fields = self._validate_data(data, fields)
        output_path = self._get_output_path(filename)

        with open(output_path, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(
                output_file, fieldnames=fields, extrasaction='ignore')
            dict_writer.writeheader()
            dict_writer.writerows(data)
