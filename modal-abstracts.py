import modal
from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict

# ------------------------------------------------------------

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

# ------------------------------------------------------------

# Build a lightweight image with required deps for web endpoints
image = modal.Image.debian_slim().pip_install(
    "fastapi[standard]",
    "pyalex",
    "typing_extensions",
).add_local_dir("static", remote_path="/root/static")


app = modal.App("love-you-kiren", image=image)


@app.function()
@modal.asgi_app()
def fastapi_app():
    # Import inside the function so they resolve within the Modal container
    from fastapi import FastAPI
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
    # from .abstracts import fetch_paper_metadata

    web_app = FastAPI()

    # Optional: serve the existing static UI if present
    web_app.mount("/static", StaticFiles(directory="/root/static"), name="static")

    @web_app.get("/get")
    def get_abstract(url: str):
        return fetch_paper_metadata(url)

    @web_app.get("/", include_in_schema=False)
    def index():
        return FileResponse("/root/static/index.html")

    return web_app
