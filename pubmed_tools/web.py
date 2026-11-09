"""The DOI lookup page: `kiren-web` serves it on http://127.0.0.1:8000 (needs the web extra)."""

import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .openalex import PaperNotFound, fetch_paper_metadata

INDEX_HTML = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")

app = FastAPI(title="kiren")


@app.get("/get")
def get_abstract(url: str) -> dict[str, Any]:
    try:
        return fetch_paper_metadata(url)
    except PaperNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"OpenAlex request failed: {exc}") from exc


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(INDEX_HTML)


def run() -> None:
    import uvicorn

    uvicorn.run(app, host=os.getenv("KIREN_HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8000")))
