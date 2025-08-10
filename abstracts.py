"""
Fetch and print the abstract and selected metadata of a paper given a URL using pyalex.

Usage:
    python abstracts.py --url "https://doi.org/10.1093/scan/nsq093"
"""

import argparse
import sys
import json
from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict


class PaperMetadata(TypedDict, total=False):
    title: str
    publication_date: str
    authors: List[str]
    keywords: List[str]
    cited_by_count: Optional[int]
    abstract: Optional[str]
    url: str


def get_authors(authorships: List[Dict[str, Any]]) -> List[str]:
    """Extract author names from OpenAlex authorships data."""
    authors = []
    for authorship in authorships:
        author = authorship.get("author", {})
        name = author.get("display_name") or author.get("name")
        if name:
            authors.append(name)
    return authors


def get_keywords(result: Dict[str, Any]) -> List[str]:
    """Extract keywords from OpenAlex data, trying keywords then concepts."""
    if "keywords" in result and isinstance(result["keywords"], list):
        return [k.get("display_name") for k in result["keywords"] if k.get("display_name")]
    
    if "concepts" in result and isinstance(result["concepts"], list):
        return [c.get("display_name") for c in result["concepts"] if c.get("display_name")]
    
    return []


def reconstruct_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
    """Reconstruct abstract text from OpenAlex inverted index format."""
    if not isinstance(inverted_index, dict):
        return None
    
    # Find maximum position to determine array size
    max_position = -1
    for positions in inverted_index.values():
        if positions:
            max_position = max(max_position, max(positions))
    
    if max_position < 0:
        return None
    
    # Place words at their correct positions
    words = [None] * (max_position + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            words[pos] = word
    
    return " ".join(word for word in words if word is not None)


def get_abstract(result: Dict[str, Any]) -> Optional[str]:
    """Extract abstract from OpenAlex result with multiple fallback strategies."""
    # Try direct abstract field
    abstract = result.get("abstract")
    if abstract:
        return abstract
    
    # Try reconstructing from inverted index
    inverted_index = result.get("abstract_inverted_index")
    abstract = reconstruct_abstract(inverted_index)
    if abstract:
        return abstract
    
    # Try v3 inverted index
    inverted_index_v3 = result.get("abstract_inverted_index_v3")
    abstract = reconstruct_abstract(inverted_index_v3)
    if abstract:
        return abstract
    
    # Try other description fields
    return result.get("description") or result.get("summary")


def fetch_paper_metadata(url: str) -> PaperMetadata:
    """Fetch paper metadata from OpenAlex using pyalex."""
    try:
        from pyalex import Works
    except ImportError:
        raise ImportError("pyalex is not installed. Please install it with 'pip install pyalex'.")
    
    works = Works()
    result = works[url]
    
    if not isinstance(result, dict):
        raise ValueError("Unexpected result format from pyalex.")
    
    return {
        "title": result.get("title") or result.get("display_name"),
        "publication_date": result.get("publication_date") or str(result.get("publication_year") or ""),
        "authors": get_authors(result.get("authorships", [])),
        "keywords": get_keywords(result),
        "cited_by_count": result.get("cited_by_count"),
        "abstract": get_abstract(result),
        "url": url,
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch abstract and metadata from a paper URL using pyalex.")
    parser.add_argument("--url", required=True, help="URL of the paper (e.g., DOI link)")
    args = parser.parse_args()

    try:
        metadata = fetch_paper_metadata(args.url)
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
    except ImportError as e:
        print(f"Import error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching paper metadata: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()