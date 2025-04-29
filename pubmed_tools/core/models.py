from typing import TypedDict, List, Union


class ArticleDetails(TypedDict):
    """Schema for parsed article details.

    Fields:
        title: Article title as string
        abstract: Full abstract text as string
        authors: List of author names as strings
        publication_date: Defaults to dict with keys 'year', 'month', 'day'.
                           If convert_date=True, value is a string in the format YYYY-MM-DD
        pmid: PubMed ID as string
    """
    title: str
    abstract: str
    authors: List[str]
    publication_date: Union[str, dict]
    pmid: str


class SearchResult(TypedDict):
    """Schema for PubMed search results."""
    id_list: List[str]
    count: str
    webenv: str
    query_key: str
