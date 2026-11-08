# kiren

Search PubMed and save the matching articles (title, abstract, authors,
publication date, PMID) as CSV, Excel or PDF, or look up one paper by DOI.
PubMed goes through NCBI's E-utilities and DOIs through OpenAlex; neither needs
an account.

## Quick start

Needs [uv](https://docs.astral.sh/uv/) 0.13 or newer; uv installs Python 3.11+ if needed.

```bash
git clone https://github.com/TanGentleman/kiren && cd kiren
uv sync --locked
uv run kiren "chunking memory" --csv --pdf --max-results 20   # writes outputs/output.csv and outputs/output.pdf
uv run kiren-doi https://doi.org/10.1093/scan/nsq093          # metadata as JSON
```

Without uv: `python3 -m venv .venv && .venv/bin/pip install -e .` (add `.[web]` for `kiren-web`).

## Commands

| Command | What it does |
| --- | --- |
| `kiren QUERY --csv\|--xlsx\|--pdf\|--all [--max-results N] [--out DIR]` | Search PubMed, write `output.<format>` to `DIR` (default `./outputs`). At least one format. `--max-results` defaults to 100. |
| `kiren-doi URL` | Print title, date, authors, keywords, citation count and abstract as JSON. |
| `kiren-web` | Serve the same DOI lookup as a page on http://127.0.0.1:8000. Needs `uv sync --extra web`. |

`QUERY` uses PubMed syntax, e.g. `"fasting[ti] AND 2023[dp]"`. In CSV and Excel,
authors are joined with `; ` and dates are `YYYY-MM-DD`, `YYYY-MM` or `YYYY`,
depending on what PubMed has.

| Exit code | `kiren` | `kiren-doi` |
| --- | --- | --- |
| 0 | exported, or no results (nothing written) | printed |
| 1 | PubMed request or an export failed | not found, or OpenAlex request failed |
| 2 | bad usage | bad usage |

`kiren-web` answers `/get?url=<doi url>` with 200, 404 (unknown DOI) or 502
(OpenAlex unreachable).

## Python

```python
from pubmed_tools import ArticleParser, CSVExporter, PubMedClient

client = PubMedClient()
raw = client.search_and_fetch("chunking memory", max_results=20)
articles = ArticleParser.parse_all_details(raw)
print(articles[0]["title"], articles[0]["authors"])
CSVExporter().export(articles, "/tmp/chunking.csv")
```

The distribution is `kiren`; the import name is `pubmed_tools`.

## Environment variables

| Variable | Default | Effect |
| --- | --- | --- |
| `NCBI_API_KEY` | none | Raises NCBI's limit from 3 to 10 requests/s ([get one](https://support.nlm.nih.gov/kbArticle/?pn=KA-05317)). |
| `NCBI_EMAIL` | none | Sent to NCBI so they can contact you about heavy use. |
| `PUBMED_TOOLS_OUTPUT_DIR` | `outputs` | Default for `kiren --out`, and where relative export filenames go in the Python API. |
| `KIREN_EUTILS_URL` | NCBI | E-utilities base URL; the tests point it at a local fake. |
| `KIREN_OPENALEX_URL` | `https://api.openalex.org` | OpenAlex base URL. |
| `KIREN_HOST`, `PORT` | `127.0.0.1`, `8000` | Where `kiren-web` listens. |

## Boundaries

- Network: `kiren` calls NCBI E-utilities, `kiren-doi` and `kiren-web` call
  OpenAlex. Requests time out after 30 s. Nothing else is contacted.
- No credentials are required. `NCBI_API_KEY` is optional.
- `kiren-web` binds 127.0.0.1. Upstream's Modal deployment of the page was
  removed; no hosted version is maintained here.

## Development

```bash
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest                # offline: local fake NCBI and OpenAlex servers replay tests/fixtures
uv run kiren --help
tests/fixtures/record.sh     # re-record the fixtures from NCBI and OpenAlex (needs network)
```

CI (`.github/workflows/ci.yml`) runs the first five commands on Python 3.11 to
3.15. `uv.lock` pins exact versions; the floors in `pyproject.toml` are the
versions it was last tested with. pytest treats warnings as errors.
