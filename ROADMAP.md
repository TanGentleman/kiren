# kiren roadmap

kiren is a small Python SDK (`pubmed_tools`) that searches PubMed through NCBI's
E-utilities, parses each record into `title / abstract / authors / publication_date /
pmid`, and exports the results to CSV, Excel or PDF. It was written in 2024-11 as a
research helper for Kiren; a 2025-08 add-on looks up a paper's metadata by DOI through
OpenAlex and serves it on a small web page.

Verdict: worth reviving. The core is about 500 lines with a clear shape and still works
against the live E-utilities API. Most of the repo around it was noise.

## Upstream status (main af1e1e4, checked 2026-11-08)

- Last commit 2025-08-10. No CI, lockfile or package data for the PDF font.
- `pip install -e .` on Python 3.12: 12 tests passed, 1 failed (`No module named
  'openpyxl'`). README claimed 94% coverage; measured 85%.
- A live run of `pubmed_tools/examples/basic_usage.py` exported CSV, XLSX and PDF.
- `abstracts.py` needs `typing_extensions` besides `pyalex`; `kiren-api.py` needs
  `fastapi` and `uvicorn`, which no file listed.
- No credentials in the history (`git log --all -p`).
- Open issues: #3 type mismatches with `ArticleDetails`, #5 Sci-Hub support, #6 resolve DOIs.

Bugs found by running it, all fixed on `kiren-1` or `kiren-3` with a test: titles and
abstracts with inline markup lost or reordered words; PDF export parsed text as
ReportLab markup; CSV/Excel cells held Python reprs; dates like `2023-Sep-`;
`<CollectiveName>` authors became empty; `fetch_details` returned `[]` on HTTP errors
and had no timeout; `from pubmed_tools.core import *` raised; `<PMID>` without
`Version` raised; searches and efetches with no hits raised `AttributeError`.

## Stack

Each branch is based on the previous one.

- `kiren-1`: import, the bug fixes above, recorded efetch fixture, this file.
- `kiren-2`: installable package (distribution `kiren`, import name `pubmed_tools`),
  font as package data, `kiren` command with `--out`, `setup.py` and `requirements*.txt`
  removed, `uv.lock`, ruff.
- `kiren-3`: client and CLI tests over HTTP against a fake E-utilities server replaying
  responses recorded by `tests/fixtures/record.sh`; `NCBI_API_KEY`, `NCBI_EMAIL`,
  `KIREN_EUTILS_URL`; CI.
- `kiren-4`: cut both notebooks, `examples/demo.py`, `modal-abstracts.py`, unused
  `SearchResult`; new README.
- `kiren-5`: OpenAlex DOI lookup in the package as `kiren-doi` and `kiren-web`
  (`web` extra), binding 127.0.0.1 and returning 404/502 instead of 500.
- `kiren-6`: Python 3.10 dropped (EOL 2026-10-01; it held pandas at 2.3.3), every
  dependency at its latest release (pandas 3.1.1, reportlab 5.1.0, fastapi 0.162.2,
  starlette 1.10.0, pytest 9.2.0, ...) with matching pyproject floors; dev tests use
  `httpx2` because starlette 1.10 deprecates `httpx` in its TestClient; pytest treats
  warnings as errors. CI on Python 3.11-3.15 with uv 0.13.7 and SHA-pinned actions.
  Tests for kiren-web's 502, kiren-doi's and kiren's exit 1. README rewritten around
  command, exit-code and env-var tables. The quick start, `kiren-doi` and `kiren-web`
  were run live against NCBI and OpenAlex on 2026-11-08.
- `kiren-7`: README cut to 25 words; details moved to IMPLEMENTATION.md.

Not done, because they need Tan: replacing pandas with plain openpyxl (drops pandas and
numpy, changes Excel cell typing), a combined `kiren search|doi` command, Sci-Hub support
(issue #5, legal question), and a hosted deployment of the page.

## Needs Tan

- License: upstream has none, so `pyproject.toml` declares none. Pick one before
  publishing.
- Behavior changes to accept: `fetch_details` raises on HTTP errors instead of returning
  `[]`; CSV/Excel cells and dates are plain text (`A; B`, `2023-09`); `kiren-web` listens
  on 127.0.0.1 (set `KIREN_HOST=0.0.0.0` to expose it like upstream did); Python 3.10 is
  no longer supported (`kiren-6`).
- Renaming the import package `pubmed_tools` to `kiren` would break existing code; not done.
- CI has not run on GitHub (nested workflows don't run in kranti-sandbox); the same
  commands pass locally on 3.11-3.15. Check the first Actions run after applying.
