# kiren

Search PubMed and save the matching articles (title, abstract, authors, publication date,
PMID) as CSV, Excel or PDF. It uses NCBI's free E-utilities API; no account is needed.

## Install

Python 3.10 or newer.

```bash
git clone https://github.com/TanGentleman/kiren && cd kiren
uv sync                      # or: python3 -m venv .venv && .venv/bin/pip install -e .
```

## Use it from the shell

```bash
uv run kiren "chunking memory" --csv --pdf --max-results 20
# writes outputs/output.csv and outputs/output.pdf
uv run kiren "cancer immunotherapy" --all --out results/
```

`--csv`, `--xlsx`, `--pdf` or `--all` picks the formats (at least one). The query uses
PubMed syntax, e.g. `"fasting[ti] AND 2023[dp]"`. Authors are joined with `; ` and dates
are `YYYY-MM-DD` (or `YYYY-MM`, `YYYY` when PubMed has less).

## Use it from Python

```python
from pubmed_tools import ArticleParser, CSVExporter, PubMedClient

client = PubMedClient()
raw = client.search_and_fetch("chunking memory", max_results=20)
articles = ArticleParser.parse_all_details(raw)
print(articles[0]["title"], articles[0]["authors"])
CSVExporter().export(articles, "/tmp/chunking.csv")
```

## Settings

| Variable | Default | Purpose |
| --- | --- | --- |
| `NCBI_API_KEY` | none | Raises NCBI's limit from 3 to 10 requests/s ([get one](https://support.nlm.nih.gov/kbArticle/?pn=KA-05317)) |
| `NCBI_EMAIL` | none | Sent to NCBI so they can contact you about heavy use |
| `PUBMED_TOOLS_OUTPUT_DIR` | `outputs` | Where relative export filenames go |
| `KIREN_EUTILS_URL` | NCBI | E-utilities base URL (the tests point it at a local fake) |

## Development

```bash
uv sync --locked
uv run pytest                # offline: a local fake E-utilities server replays tests/fixtures
uv run ruff check . && uv run ruff format --check .
tests/fixtures/record.sh     # re-record the fixtures from NCBI (needs network)
```

`abstracts.py` and `kiren-api.py` are a separate DOI lookup through OpenAlex
(`pip install pyalex typing_extensions fastapi uvicorn`, then `python abstracts.py --url
https://doi.org/10.1093/scan/nsq093`).
