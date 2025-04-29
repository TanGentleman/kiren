"""
Basic PubMed Tools Usage Example

This script demonstrates how to search PubMed, parse articles, and export results
in various formats (CSV, Excel, PDF).

Usage:
    python basic_usage.py "search query" [--csv] [--xlsx] [--pdf] [--all] [--max-results N]

Arguments:
    query           Search query for PubMed (default: "nutrition fasting")

Export options (at least one required):
    --csv           Export results to CSV
    --xlsx          Export results to Excel (.xlsx)
    --pdf           Export results to PDF
    --all           Export results to all formats

Other options:
    --max-results N Maximum number of articles to fetch (default: 100)

Example:
    python basic_usage.py "cancer immunotherapy" --csv --pdf --max-results 50
"""

import argparse
import logging
from typing import List

from pubmed_tools.core.client import PubMedClient
from pubmed_tools.parsers.article import ArticleParser
from pubmed_tools.exporters.csv_exporter import CSVExporter
from pubmed_tools.exporters.excel_exporter import ExcelExporter
from pubmed_tools.exporters.pdf_exporter import PDFExporter


def setup_logging() -> None:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def main(
    query: str,
    export_csv: bool,
    export_xlsx: bool,
    export_pdf: bool,
    max_results: int
) -> None:
    """
    Search PubMed, parse articles, and export results in selected formats.

    Args:
        query (str): Search query for PubMed.
        export_csv (bool): Whether to export results to CSV.
        export_xlsx (bool): Whether to export results to Excel.
        export_pdf (bool): Whether to export results to PDF.
        max_results (int): Maximum number of articles to fetch.
    """
    client = PubMedClient()
    parser = ArticleParser()

    try:
        logging.info(f"Searching PubMed for: '%s' (max %d results)...", query, max_results)
        results = client.search(query, use_history=False, retmax=max_results)
        id_list: List[str] = results.get("id_list", [])
        if not id_list:
            logging.warning("No articles found for this query.")
            return
        details = client.fetch_details(id_list=id_list)

        parsed_articles = parser.parse_all_details(details)
        if not parsed_articles:
            logging.warning("No articles could be parsed.")
            return

        exporters = []
        if export_csv:
            exporters.append(('csv', CSVExporter()))
        if export_xlsx:
            exporters.append(('xlsx', ExcelExporter()))
        if export_pdf:
            exporters.append(('pdf', PDFExporter()))

        for format_name, exporter in exporters:
            filename = f"output.{format_name}"
            try:
                exporter.export(parsed_articles, filename)
                logging.info("Exported to %s", filename)
            except Exception as e:
                logging.error("Failed to export to %s: %s", filename, e)
    except Exception as exc:
        logging.error("An error occurred: %s", exc)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Search and export PubMed articles to various formats.'
    )
    parser.add_argument('query', nargs='?', default="nutrition fasting",
                        help='Search query for PubMed (default: "nutrition fasting")')
    parser.add_argument('--csv', action='store_true', help='Export results to CSV')
    parser.add_argument('--xlsx', action='store_true', help='Export results to Excel (.xlsx)')
    parser.add_argument('--pdf', action='store_true', help='Export results to PDF')
    parser.add_argument('--all', action='store_true', help='Export results to all formats')
    parser.add_argument('--max-results', type=int, default=100,
                        help='Maximum number of articles to fetch (default: 100)')
    return parser.parse_args()


def run() -> None:
    """Entry point for running as a script."""
    setup_logging()
    args = parse_args()

    export_csv = args.csv or args.all
    export_xlsx = args.xlsx or args.all
    export_pdf = args.pdf or args.all

    if not (export_csv or export_xlsx or export_pdf):
        logging.error("At least one export format must be specified (use --csv, --xlsx, --pdf, or --all).")
        print()  # For argparse help formatting
        parse_args().print_help()
        exit(1)

    main(args.query, export_csv, export_xlsx, export_pdf, args.max_results)


if __name__ == "__main__":
    run()
