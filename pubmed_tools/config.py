import os

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# Relative export filenames go here; override with PUBMED_TOOLS_OUTPUT_DIR or `kiren --out`.
OUTPUT_DIR = os.getenv('PUBMED_TOOLS_OUTPUT_DIR', 'outputs')

# Unicode font for PDF export (names and symbols outside Latin-1)
PDF_FONT_PATH = os.path.join(PACKAGE_DIR, 'fonts', 'DejaVuSans.ttf')
