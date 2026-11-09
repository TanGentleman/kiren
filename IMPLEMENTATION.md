# kiren: implementation

## Requirements

- Python 3.11+ and [uv](https://docs.astral.sh/uv/) 0.13 or newer. Without uv:
  `python3 -m venv .venv && .venv/bin/pip install -e .` (add `.[web]` for `kiren-web`).
- Network: `kiren` calls NCBI E-utilities; `kiren-doi` and `kiren-web` call OpenAlex. Neither
  needs an account; `NCBI_API_KEY` is optional.
- `kiren-web` needs the `web` extra: `uv sync --extra web`.

## Usage

| Command | What it does |
| --- | --- |
| `kiren QUERY --csv\|--xlsx\|--pdf\|--all [--max-results N] [--out DIR]` | Search PubMed, write `output.<format>` to `DIR` (default `./outputs`). At least one format. `--max-results` defaults to 100. |
| `kiren-doi URL` | Print title, date, authors, keywords, citation count and abstract as JSON. |
| `kiren-web` | Serve the same DOI lookup as a page on http://127.0.0.1:8000. |

In a checkout, prefix them with `uv run`, e.g. `uv run kiren-doi https://doi.org/10.1093/scan/nsq093`.

`QUERY` uses PubMed syntax, e.g. `"fasting[ti] AND 2023[dp]"`. In CSV and Excel, authors are
joined with `; ` and dates are `YYYY-MM-DD`, `YYYY-MM` or `YYYY`, depending on what PubMed has.

| Exit code | `kiren` | `kiren-doi` |
| --- | --- | --- |
| 0 | exported, or no results (nothing written) | printed |
| 1 | PubMed request or an export failed | not found, or OpenAlex request failed |
| 2 | bad usage | bad usage |

`kiren-web` answers `/get?url=<doi url>` with 200, 404 (unknown DOI) or 502 (OpenAlex
unreachable).

From Python (the distribution is `kiren`; the import name is `pubmed_tools`):

```python
from pubmed_tools import ArticleParser, CSVExporter, PubMedClient

client = PubMedClient()
raw = client.search_and_fetch("chunking memory", max_results=20)
articles = ArticleParser.parse_all_details(raw)
print(articles[0]["title"], articles[0]["authors"])
CSVExporter().export(articles, "/tmp/chunking.csv")
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `NCBI_API_KEY` | none | Raises NCBI's limit from 3 to 10 requests/s ([get one](https://support.nlm.nih.gov/kbArticle/?pn=KA-05317)). |
| `NCBI_EMAIL` | none | Sent to NCBI so they can contact you about heavy use. |
| `PUBMED_TOOLS_OUTPUT_DIR` | `outputs` | Default for `kiren --out`, and where relative export filenames go in the Python API. |
| `KIREN_EUTILS_URL` | NCBI | E-utilities base URL; the tests point it at a local fake. |
| `KIREN_OPENALEX_URL` | `https://api.openalex.org` | OpenAlex base URL. |
| `KIREN_HOST`, `PORT` | `127.0.0.1`, `8000` | Where `kiren-web` listens. |

## How it works

`pubmed_tools/core/client.py` (`PubMedClient`) calls `esearch.fcgi` for PMIDs and `efetch.fcgi`
for the records, with a 30 s timeout. It flattens inline markup (`<i>`, `<sup>`) with ElementTree
before `xmltodict` parses the XML, so titles and abstracts keep their word order.

`pubmed_tools/parsers/article.py` (`ArticleParser`) turns each record into `title`, `abstract`,
`authors`, `publication_date` and `pmid`; `parsers/date.py` formats the date.
`pubmed_tools/exporters/` writes CSV, Excel (pandas) and PDF (ReportLab, with the bundled
`fonts/DejaVuSans.ttf`). `pubmed_tools/cli.py` is the `kiren` command.

`pubmed_tools/openalex.py` fetches a work from OpenAlex and rebuilds its abstract from the inverted
index (`kiren-doi`). `pubmed_tools/web.py` is a FastAPI app serving `static/index.html` and `/get`
(`kiren-web`).

## Tests

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv run kiren --help
```

CI (`.github/workflows/ci.yml`) runs these on Python 3.11 to 3.15. The tests are offline: local
fake NCBI and OpenAlex servers replay `tests/fixtures`. `tests/fixtures/record.sh` re-records the
fixtures from NCBI and OpenAlex (needs network). pytest treats warnings as errors. `uv.lock` pins
exact versions; the floors in `pyproject.toml` are the versions it was last tested with.

## Limits

- No contact with anything except NCBI E-utilities and OpenAlex.
- `kiren-web` binds 127.0.0.1. Upstream's Modal deployment of the page was removed; no hosted
  version is maintained here.
- No license yet.
