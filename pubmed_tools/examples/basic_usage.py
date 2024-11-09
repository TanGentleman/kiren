from pubmed_tools.core.client import PubMedClient
from pubmed_tools.parsers.article import ArticleParser
from pubmed_tools.exporters.csv_exporter import CSVExporter
from pubmed_tools.exporters.excel_exporter import ExcelExporter
from pubmed_tools.exporters.pdf_exporter import PDFExporter

def main(query: str = "nutrition fasting"):
    # Initialize components
    client = PubMedClient()
    parser = ArticleParser()
    
    # Search and fetch articles
    results = client.search(query)
    id_list = results["id_list"]
    details = client.fetch_details(id_list)
    
    # Parse articles
    parsed_articles = parser.parse_all_details(details)
    
    # Export to different formats
    exporters = {
        'csv': CSVExporter(),
        'excel': ExcelExporter(),
        'pdf': PDFExporter()
    }
    
    for format_name, exporter in exporters.items():
        filename = f"output.{format_name}"
        exporter.export(parsed_articles, filename)
        print(f"Exported to {filename}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Search and export PubMed articles')
    parser.add_argument('query', nargs='?', default="nutrition fasting",
                      help='Search query for PubMed')
    args = parser.parse_args()
    main(args.query) 