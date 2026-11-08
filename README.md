# PubMed Tools

A Python SDK for interacting with PubMed's API, with support for searching, parsing, and exporting research articles.

## Features

- 🔍 **Search**: Easy-to-use interface for searching PubMed articles
- 📑 **Parse**: Extract structured data from PubMed articles including titles, abstracts, authors, and dates
- 📤 **Export**: Export results to multiple formats (CSV, Excel, PDF)
- 🧪 **Well-tested**: 94% test coverage with pytest
- 📚 **Type hints**: Full typing support for better IDE integration

## Installation
1. Clone the repository:
```bash
git clone https://github.com/TanGentleman/kiren.git
```

2. Install the dependencies:
```bash
pip install -e .
```

## Usage
```bash
kiren "nutrition fasting" --csv
```

## All-in-one (Python 3.10+)
```bash
git clone https://github.com/TanGentleman/kiren.git
cd kiren
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
kiren "nutrition fasting" --csv
```

## Running after setup
```bash
cd kiren
source .venv/bin/activate
kiren "Perceptual Organization AND cerebral trauma" --pdf --csv
```