import os
import subprocess # Only to open files on macOS

from pubmed_tools.core.client import PubMedClient
from pubmed_tools.parsers.article import ArticleParser
from pubmed_tools.exporters.pdf_exporter import PDFExporter
from pubmed_tools.exporters.csv_exporter import CSVExporter

from pubmed_tools.config import OUTPUT_DIR

DEFAULT_QUERY = "longitudinal fasting"
# Configuration settings
CONFIG = {
    'exporters': {
        'pdf': {
            'enabled': True,
            'auto_open': True,
            'exporter': PDFExporter(),
        },
        'csv': {
            'enabled': False,
            'auto_open': True,
            'exporter': CSVExporter(),
        },
    },
    'truncate_articles': {
        'enabled': False,
        'count': 2,
    }
}

def open_file(filename: str) -> None:
    """Opens a file using the system's default application.

    Args:
        filename: Path to the file to open

    Note:
        This is platform-dependent and is only tested on macOS.
    """
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    valid_formats = ['.pdf', '.csv', '.xlsx']
    file_ext = os.path.splitext(filename.lower())[1]
    if file_ext not in valid_formats:
        raise ValueError(
            f"File must be one of {valid_formats}, got: {filename}")
    subprocess.Popen(f"open {filepath}", shell=True)

def main(query: str = DEFAULT_QUERY) -> dict[str, str]:
    # Initialize components
    client = PubMedClient()
    parser = ArticleParser()

    # Search and fetch articles
    results = client.search(query)
    id_list = results["id_list"]
    details = client.fetch_details(id_list)

    # Parse articles
    parsed_articles = parser.parse_all_details(details)
    if CONFIG['truncate_articles']['enabled']:
        parsed_articles = parsed_articles[:CONFIG['truncate_articles']['count']]

    # Export to different formats
    exported_files = {}
    for format_name, settings in CONFIG['exporters'].items():
        if settings['enabled']:
            # Create filename with only valid characters
            safe_query = '_'.join(query[:10].split())
            filename = f"{safe_query}-output.{format_name}"
            settings['exporter'].export(parsed_articles, filename)
            exported_files[format_name] = filename
            print(f"Exported to {filename}")

    return exported_files

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description='Search and export PubMed articles')
    parser.add_argument('query', nargs='?', default=DEFAULT_QUERY,
                       help='Search query for PubMed')
    args = parser.parse_args()
    try:
        exported_files = main(args.query)
        # Only open files that are configured for auto-opening
        for format_name, filepath in exported_files.items():
            if CONFIG['exporters'][format_name]['auto_open']:
                open_file(filepath)
    except Exception as e:
        print(f"Error! {e}")
