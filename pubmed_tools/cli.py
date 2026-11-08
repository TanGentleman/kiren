"""
kiren: search PubMed and export the articles to CSV, Excel or PDF.

Usage:
    kiren "search query" [--csv] [--xlsx] [--pdf] [--all] [--max-results N] [--out DIR]

Arguments:
    query           Search query for PubMed (default: "nutrition fasting")

Export options (at least one required):
    --csv           Export results to CSV
    --xlsx          Export results to Excel (.xlsx)
    --pdf           Export results to PDF
    --all           Export results to all formats

Other options:
    --max-results N Maximum number of articles to fetch (default: 100)
    --out DIR       Directory for output.csv / output.xlsx / output.pdf (default: ./outputs)

Example:
    kiren "cancer immunotherapy" --csv --pdf --max-results 50
"""

import argparse
import logging
import os
import sys
from typing import List, Optional, Tuple

from pubmed_tools.config import OUTPUT_DIR
from pubmed_tools.core.client import PubMedClient
from pubmed_tools.exporters.csv_exporter import CSVExporter
from pubmed_tools.exporters.excel_exporter import ExcelExporter
from pubmed_tools.exporters.pdf_exporter import PDFExporter
from pubmed_tools.parsers.article import ArticleParser


def setup_logging() -> None:
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
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
    parser.add_argument('--out', default=OUTPUT_DIR,
                        help='Output directory (default: ./outputs)')
    return parser


def main(
    query: str,
    export_csv: bool,
    export_xlsx: bool,
    export_pdf: bool,
    max_results: int,
    out_dir: str = OUTPUT_DIR,
) -> int:
    """
    Search PubMed, parse articles, and export results in selected formats.

    Returns the process exit code: 0 on success or no results, 1 if anything failed.
    """
    client = PubMedClient()
    parser = ArticleParser()

    try:
        logging.info("Searching PubMed for: '%s' (max %d results)...", query, max_results)
        results = client.search(query, use_history=False, retmax=max_results)
        id_list: List[str] = results.get("id_list", [])
        if not id_list:
            logging.warning("No articles found for this query.")
            return 0
        details = client.fetch_details(id_list=id_list)
    except Exception as exc:
        logging.error("PubMed request failed: %s", exc)
        return 1

    parsed_articles = parser.parse_all_details(details)
    if not parsed_articles:
        logging.warning("No articles could be parsed.")
        return 0

    exporters: List[Tuple[str, object]] = []
    if export_csv:
        exporters.append(('csv', CSVExporter()))
    if export_xlsx:
        exporters.append(('xlsx', ExcelExporter()))
    if export_pdf:
        exporters.append(('pdf', PDFExporter()))

    status = 0
    for format_name, exporter in exporters:
        path = os.path.abspath(os.path.join(out_dir, f"output.{format_name}"))
        try:
            exporter.export(parsed_articles, path)
            logging.info("Exported %d articles to %s", len(parsed_articles), path)
        except Exception as e:
            logging.error("Failed to export to %s: %s", path, e)
            status = 1
    return status


def run(argv: Optional[List[str]] = None) -> None:
    """Entry point for the `kiren` command."""
    setup_logging()
    parser = get_arg_parser()
    args = parser.parse_args(argv)

    export_csv = args.csv or args.all
    export_xlsx = args.xlsx or args.all
    export_pdf = args.pdf or args.all

    if not (export_csv or export_xlsx or export_pdf):
        parser.error("choose at least one export format: --csv, --xlsx, --pdf or --all")

    sys.exit(main(args.query, export_csv, export_xlsx, export_pdf, args.max_results, args.out))


if __name__ == "__main__":
    run()
