import pytest
import os
import pandas as pd
from pubmed_tools.exporters.csv_exporter import CSVExporter
from pubmed_tools.exporters.excel_exporter import ExcelExporter
from pubmed_tools.exporters.pdf_exporter import PDFExporter

@pytest.fixture
def sample_data():
    return [
        {
            'title': 'Test Article 1',
            'abstract': 'Test Abstract 1',
            'authors': ['John Doe', 'Jane Smith'],
            'publication_date': {'year': '2023', 'month': '01', 'day': '01'},
            'pmid': '12345'
        },
        {
            'title': 'Test Article 2',
            'abstract': 'Test Abstract 2',
            'authors': ['Bob Johnson'],
            'publication_date': {'year': '2023', 'month': '02', 'day': '02'},
            'pmid': '67890'
        }
    ]

@pytest.fixture
def temp_dir(tmpdir):
    return str(tmpdir)

class TestCSVExporter:
    def test_export(self, sample_data, temp_dir):
        # Arrange
        exporter = CSVExporter()
        filename = os.path.join(temp_dir, 'test.csv')
        
        # Act
        exporter.export(sample_data, filename)
        
        # Assert
        assert os.path.exists(filename)
        df = pd.read_csv(filename)
        assert len(df) == 2
        assert list(df.columns) == ['title', 'abstract', 'authors', 'publication_date', 'pmid']

    def test_export_empty_data(self):
        exporter = CSVExporter()
        with pytest.raises(ValueError, match="Data cannot be empty"):
            exporter.export([], 'test.csv')

class TestExcelExporter:
    def test_export(self, sample_data, temp_dir):
        # Arrange
        exporter = ExcelExporter()
        filename = os.path.join(temp_dir, 'test.xlsx')
        
        # Act
        exporter.export(sample_data, filename)
        
        # Assert
        assert os.path.exists(filename)
        df = pd.read_excel(filename)
        assert len(df) == 2
        assert list(df.columns) == ['title', 'abstract', 'authors', 'publication_date', 'pmid']

class TestPDFExporter:
    def test_export(self, sample_data, temp_dir):
        # Arrange
        exporter = PDFExporter()
        filename = os.path.join(temp_dir, 'test.pdf')
        
        # Act
        exporter.export(sample_data, filename)
        
        # Assert
        assert os.path.exists(filename)
        # Basic file size check to ensure PDF was created
        assert os.path.getsize(filename) > 0 