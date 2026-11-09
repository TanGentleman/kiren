from typing import TypedDict


class ArticleDetails(TypedDict):
    """Schema for parsed article details.

    Fields:
        title: Article title as string
        publication_date: Defaults to dict with keys 'year', 'month', 'day'.
                           If convert_date=True, value is a string in the format YYYY-MM-DD
        pmid: PubMed ID as string
        authors: List of author names as strings
        abstract: Full abstract text as string
    """

    title: str
    publication_date: str | dict
    pmid: str
    authors: list[str]
    abstract: str
