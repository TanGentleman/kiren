"""Look up a paper's metadata by DOI (or any id OpenAlex accepts) through OpenAlex."""

import argparse
import json
import os
import sys
from typing import Any, TypedDict
from urllib.parse import quote

import requests

OPENALEX_URL = "https://api.openalex.org"
TIMEOUT_SECONDS = 30


class PaperMetadata(TypedDict, total=False):
    title: str
    publication_date: str
    authors: list[str]
    keywords: list[str]
    cited_by_count: int | None
    abstract: str | None
    url: str


class PaperNotFound(LookupError):
    pass


def get_authors(authorships: list[dict[str, Any]]) -> list[str]:
    names = []
    for authorship in authorships:
        author = authorship.get("author") or {}
        name = author.get("display_name") or author.get("name")
        if name:
            names.append(name)
    return names


def get_keywords(work: dict[str, Any]) -> list[str]:
    """Keywords, falling back to concepts."""
    for field in ("keywords", "concepts"):
        if isinstance(work.get(field), list):
            return [k["display_name"] for k in work[field] if k.get("display_name")]
    return []


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str | None:
    """OpenAlex stores abstracts as {word: [positions]}; put the words back in order."""
    if not isinstance(inverted_index, dict):
        return None
    positions = {pos: word for word, places in inverted_index.items() for pos in places}
    if not positions:
        return None
    return " ".join(positions[pos] for pos in sorted(positions))


def get_abstract(work: dict[str, Any]) -> str | None:
    return (
        work.get("abstract")
        or reconstruct_abstract(work.get("abstract_inverted_index"))
        or reconstruct_abstract(work.get("abstract_inverted_index_v3"))
        or work.get("description")
        or work.get("summary")
    )


def fetch_paper_metadata(url: str, base_url: str | None = None) -> PaperMetadata:
    """Metadata for a DOI URL such as https://doi.org/10.1093/scan/nsq093.

    `base_url` defaults to $KIREN_OPENALEX_URL or the public OpenAlex API.
    Raises PaperNotFound if OpenAlex has no such work.
    """
    base_url = (base_url or os.getenv("KIREN_OPENALEX_URL") or OPENALEX_URL).rstrip("/")
    response = requests.get(f"{base_url}/works/{quote(url, safe=':/')}", timeout=TIMEOUT_SECONDS)
    if response.status_code == 404:
        raise PaperNotFound(f"OpenAlex has no work for {url}")
    response.raise_for_status()
    work = response.json()
    return {
        "title": work.get("title") or work.get("display_name"),
        "publication_date": work.get("publication_date") or str(work.get("publication_year") or ""),
        "authors": get_authors(work.get("authorships") or []),
        "keywords": get_keywords(work),
        "cited_by_count": work.get("cited_by_count"),
        "abstract": get_abstract(work),
        "url": url,
    }


def run(argv: list[str] | None = None) -> None:
    """Entry point for the `kiren-doi` command: print the metadata as JSON."""
    parser = argparse.ArgumentParser(
        prog="kiren-doi", description="Look up a paper by DOI URL via OpenAlex."
    )
    parser.add_argument("url", help="e.g. https://doi.org/10.1093/scan/nsq093")
    args = parser.parse_args(argv)
    try:
        metadata = fetch_paper_metadata(args.url)
    except (PaperNotFound, requests.RequestException) as exc:
        print(f"kiren-doi: {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(metadata, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
