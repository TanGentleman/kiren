# kiren

Searches PubMed and saves the matching articles as CSV, Excel or PDF, or looks up one paper by
DOI. Needs network (NCBI, OpenAlex), no account.

```bash
git clone https://github.com/TanGentleman/kiren && cd kiren
uv sync --locked
uv run kiren "chunking memory" --csv --max-results 20   # writes outputs/output.csv
```

Needs [uv](https://docs.astral.sh/uv/) 0.13+, which installs Python 3.11+ if needed. Details:
[IMPLEMENTATION.md](IMPLEMENTATION.md), [ROADMAP.md](ROADMAP.md).
