import os

# Get the repository root directory
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Allow override via environment variable, defaulting to absolute path in project root
OUTPUT_DIR = os.getenv('PUBMED_TOOLS_OUTPUT_DIR', 
                      os.path.abspath(os.path.join(REPO_ROOT, 'outputs')))

# Path to the DejaVuSans font file
PDF_FONT_PATH = os.path.join(REPO_ROOT, 'pubmed_tools', 'fonts', 'DejaVuSans.ttf')

# Ensure the output directory is created
os.makedirs(OUTPUT_DIR, exist_ok=True)