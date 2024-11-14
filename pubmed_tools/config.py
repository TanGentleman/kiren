import os

# Allow override via environment variable, defaulting to absolute path in project root
OUTPUT_DIR = os.getenv('PUBMED_TOOLS_OUTPUT_DIR', 
                      os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs')))

# Ensure the output directory is created
os.makedirs(OUTPUT_DIR, exist_ok=True)