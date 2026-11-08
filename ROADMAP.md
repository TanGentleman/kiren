# kiren roadmap

kiren is a small Python SDK (`pubmed_tools`) that searches PubMed through NCBI's
E-utilities, parses each record into `title / abstract / authors / publication_date /
pmid`, and exports the results to CSV, Excel or PDF. It was written in 2024-11 as a
research helper for Kiren (see the `notebook.ipynb` greeting); a 2025-08 add-on looks up
a paper's metadata by DOI through OpenAlex and serves it on a small web page.

Verdict: worth reviving. The core is about 500 lines with a clear shape, it still works
against the live E-utilities API, and the bugs are small and fixable with tests. Most of
the repo around it is noise.

## Status (upstream main af1e1e4, checked 2026-11-08)

- Last commit 2025-08-10. No CI, lockfile or package data for the PDF font.
- `pip install -e .` on Python 3.12 installs requests, xmltodict, pandas 3.1.1 and
  reportlab 5.1.0. `pytest`: 12 passed, 1 failed (Excel export, `No module named
  'openpyxl'`). With openpyxl installed: 13 passed, 85% coverage (README says 94%).
- Live run works: `python pubmed_tools/examples/basic_usage.py "Perceptual Organization
  AND cerebral trauma" --all --max-results 5` exported 4 articles to `outputs/` as CSV,
  XLSX and PDF.
- `abstracts.py --url https://doi.org/10.1093/scan/nsq093` works once `pyalex` and
  `typing_extensions` are installed (only `pyalex` is in requirements.txt).
  `kiren-api.py` needs `fastapi` and `uvicorn`, which no file lists.
- No credentials in the history (`git log --all -p`). The agent notebook reads
  `TOGETHER_API_KEY` from the environment.
- Open issues: #3 type mismatches with `ArticleDetails`, #5 Sci-Hub support, #6 resolve DOIs.

### Bugs found by running it (fixed on `kiren-1`, each with a test)

- Titles and abstracts with inline markup (`<i>`, `<sup>`, ...) came out reordered or
  with words missing: xmltodict splits the tags from the text, so PMID 38860195's title
  read "Drosophila melanogaster Wolbachia Laboratory Rearing for -Based Control ..." and
  the live run above had an abstract starting with ". Headache" instead of
  "Background/Objectives. Headache". `fetch_details` now flattens those elements with
  ElementTree before xmltodict.
- PDF export parsed text as reportlab markup: an abstract with `x<y and y>z<w` dropped
  the article (and failed the export when it was the only one), `<NaN>` vanished.
- CSV and Excel cells held Python reprs: `['John Doe', 'Jane Smith']` and
  `{'year': '2023', ...}`. Now `John Doe; Jane Smith` and `2023-01-01`.
- Dates came out as `2023-Sep-` or `2020--`; now `2023-09` and `2020`.
- Consortium authors (`<CollectiveName>`) became empty strings.
- `fetch_details` returned `[]` on any HTTP error, which looks like "no results"; it now
  raises like `search` does. Both requests have a 30 s timeout (they had none).
- `from pubmed_tools.core import *` raised (`__all__` named a missing `PubMed`).
- `<PMID>` without a `Version` attribute raised `AttributeError`; `parse_all_details`
  could return `None` entries that crashed every exporter.
- `pyproject.toml` lacked `openpyxl` and claimed Python 3.7; the code needs 3.10
  (`dict | str` annotations).

### Still broken or stale

- `config.py` creates `<checkout>/outputs` at import time and finds the font relative to
  the checkout. A non-editable install writes into site-packages and has no font.
- `setup.py` disagrees with `pyproject.toml` (it depends on `pubmed_sdk`, removed in
  4a4b81b); `requirements.txt` lists `pyalex` but not `openpyxl`.
- The only CLI is `pubmed_tools/examples/basic_usage.py`; `demo.py` duplicates it and
  opens files with macOS `open`.
- Tests patch `requests.get` with hand-written XML; nothing runs the real request path
  against recorded responses.
- No NCBI `api_key`/`email`/`tool` parameters, so every user shares the 3 requests/s
  anonymous limit.
- `modal-abstracts.py` is a pasted copy of `abstracts.py` plus a Modal app.

## Signal vs noise

Keep: `PubMedClient` (search, fetch, search_and_fetch), `ArticleParser`, the three
exporters, the DejaVu font (needed for non-Latin names in PDFs), the CLI flags from
`basic_usage.py`, and the OpenAlex DOI lookup (`abstracts.py`, relevant to issue #6).

Cut: `notebook.ipynb` (a copy of `demo.py`), `agent-cookbook.ipynb` (an unrelated
smolagents joke-agent demo), `demo.py`, `setup.py`, `requirements*.txt`,
`modal-abstracts.py` (duplicate), the unused `SearchResult` TypedDict.

## Stack

Each branch is based on the previous one.

- `kiren-1` (done): import, the fixes above, `pubmed_tools/tests/fixtures/efetch.xml`
  (three real efetch records, `PubmedData` trimmed), this file.
- `kiren-2` (done): installable package. PEP 621 metadata (distribution `kiren`, import
  name still `pubmed_tools`) with the font as package data, checked in a built wheel on
  Python 3.10; `setup.py` and `requirements*.txt` removed. A `kiren` command replaces
  `examples/basic_usage.py`, adds `--out DIR` (default `./outputs`, nothing created at
  import) and exits 1 when PubMed or an export fails. Tests move to `tests/`. `uv.lock`
  (pandas 2.3.3 on 3.10, 3.1.1 on 3.11+), ruff format and lint.
- `kiren-3` (done): client and CLI tests go over real HTTP to a fake E-utilities
  server (`tests/conftest.py`) that replays responses recorded from NCBI by
  `tests/fixtures/record.sh` (re-run 2026-11-08: identical apart from the WebEnv id).
  `PubMedClient(base_url, api_key, email, tool)` reads `KIREN_EUTILS_URL`,
  `NCBI_API_KEY` and `NCBI_EMAIL`. The recorded no-results responses exposed two more
  crashes, now fixed: any search with no hits raised `AttributeError` (NCBI sends
  `<IdList/>`), and so did an efetch with no records. CI: ruff, pytest and
  `kiren --help` on Python 3.10-3.14 (`actions/checkout@v6`, `astral-sh/setup-uv@v10.3.3`;
  both refs checked with `gh api`). 39 tests pass locally on 3.10, 3.11, 3.12, 3.13, 3.14.
- `kiren-4` (done): cut both notebooks, `examples/demo.py`, `modal-abstracts.py`, the
  unused `SearchResult` and the parser's dead inline-markup branch; new README. Its
  shell and Python examples were run live against NCBI on 2026-11-08 (20 articles).
- `kiren-5` (done): the OpenAlex DOI lookup moves into the package as `kiren-doi <url>`
  (plain requests, no pyalex; live output identical to upstream `abstracts.py` for
  10.1093/scan/nsq093) and `kiren-web` (optional `web` extra: fastapi, uvicorn) serving
  the unchanged `static/index.html`. `abstracts.py`, `kiren-api.py` and `static/` are
  gone. The page binds 127.0.0.1 instead of 0.0.0.0 and returns 404/502 instead of 500.
  48 tests pass on Python 3.10, 3.11, 3.12, 3.13 and 3.14.

Stopped here. Not done, because they are not high-confidence without Tan: replacing
pandas with plain openpyxl (pandas is only used for the Excel export; it would drop
pandas and numpy, but changes cell typing), a combined `kiren search|doi` command,
Sci-Hub support (issue #5, legal question), and Modal deployment of the page.

Size: upstream has 32 files, 1,382 lines of Python (tests included) and two notebooks
(66 KB). `kiren-5` has 38 files: 872 lines of package Python and 569 lines of tests; the
added files are tests, recorded fixtures, `uv.lock`, CI and this file. The cut is the
notebooks, three duplicate scripts, `setup.py` and both requirements files.

## Apply a branch upstream

```bash
# in a kranti-sandbox clone: everything after the import commit
git fetch origin
base=$(git log -1 --format=%H --grep='^Import kiren upstream' origin/kiren-1)
git format-patch --relative=kiren "$base"..origin/kiren-1 -o /tmp/kiren-1
# in a clean upstream clone at af1e1e4
git clone https://github.com/TanGentleman/kiren && cd kiren
git am /tmp/kiren-1/*.patch
python3 -m venv .venv && .venv/bin/pip install -e . pytest pytest-cov pypdf
.venv/bin/python -m pytest -q        # kiren-1
uv sync --locked && uv run pytest    # kiren-2 and later
```

For a later branch use the same `$base` and `origin/kiren-N` to get the whole stack, or
`origin/kiren-(N-1)..origin/kiren-N` to apply one branch on top of the previous.

## Needs Tan

- License: upstream has none, so `pyproject.toml` declares none. Pick one before
  publishing.
- Naming: the distribution is now `kiren` (commands `kiren`, `kiren-doi`, `kiren-web`)
  while the import name stays `pubmed_tools`, so existing code keeps working. Renaming
  the import package is a breaking change and not done.
- Behavior changes to accept: `fetch_details` raises on HTTP errors instead of returning
  `[]`; CSV/Excel cells and dates are plain text (`A; B`, `2023-09`); `kiren-web` listens
  on 127.0.0.1 by default (set `KIREN_HOST=0.0.0.0` to expose it like upstream did).
- Live services: tests never touch NCBI or OpenAlex. A free NCBI API key (NCBI account)
  is only needed above 3 requests/s. Deploying the page (upstream's Modal app) needs your
  Modal account; the stack keeps it local only.
- Not done on purpose: dropping pandas for openpyxl, Sci-Hub support (issue #5).
