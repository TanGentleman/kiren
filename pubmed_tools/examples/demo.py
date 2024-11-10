import os
import subprocess # Only to open files on macOS

from pubmed_tools.core.client import PubMedClient
from pubmed_tools.parsers.article import ArticleParser
from pubmed_tools.exporters.pdf_exporter import PDFExporter
from pubmed_tools.exporters.csv_exporter import CSVExporter

TRUNCATE_ARTICLE = False
TRUNCATE_ARTICLE_COUNT = 2

def open_file(filename: str) -> None:
    """Opens a file using the system's default application.

    Args:
        filename: Path to the file to open

    Note:
        This is platform-dependent and is only tested on macOS.
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")

    valid_formats = ['.pdf', '.csv', '.xlsx']
    file_ext = os.path.splitext(filename.lower())[1]
    if file_ext not in valid_formats:
        raise ValueError(
            f"File must be one of {valid_formats}, got: {filename}")
    subprocess.Popen(f"open {filename}", shell=True)

def main(query: str = "nutrition fasting") -> dict[str, str]:
    # Initialize components
    client = PubMedClient()
    parser = ArticleParser()

    # Search and fetch articles
    results = client.search(query)
    id_list = results["id_list"]
    details = client.fetch_details(id_list)

    # Parse articles
    parsed_articles = parser.parse_all_details(details)
    if TRUNCATE_ARTICLE:
        parsed_articles = parsed_articles[:TRUNCATE_ARTICLE_COUNT]

    # Export to different formats
    exporters = {
        'pdf': PDFExporter(),
        'csv': CSVExporter(),
    }

    exported_files = {}
    for format_name, exporter in exporters.items():
        filename = f"output.{format_name}"
        exporter.export(parsed_articles, filename)
        exported_files[format_name] = filename
        print(f"Exported to {filename}")

    return exported_files


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Search and export PubMed articles')
    parser.add_argument('query', nargs='?', default="nutrition fasting",
                        help='Search query for PubMed')
    args = parser.parse_args()
    try:
        exported_files = main(args.query)
        open_file(exported_files['pdf'])
        open_file(exported_files['csv'])
    except Exception as e:
        print(f"Error! {e}")
