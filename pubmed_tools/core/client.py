"""
PubMed API Client

This module provides a minimal client for interacting with the PubMed API.
It allows searching for articles and fetching their raw details as dictionaries.

Note:
    This client returns raw PubMed article data (as parsed XML dicts).
    For structured parsing and normalization, use `ArticleParser` from
    `pubmed_tools.parsers.article`.

Example:
    from pubmed_tools.core.client import PubMedClient
    from pubmed_tools.parsers.article import ArticleParser

    client = PubMedClient()
    search_results = client.search("cancer treatment")
    articles_raw = client.fetch_details(id_list=search_results['id_list'])
    articles = ArticleParser.parse_all_details(articles_raw)
"""

import os
import xml.etree.ElementTree as ET
from typing import Any

import requests
import xmltodict

TIMEOUT_SECONDS = 30

# Elements whose inline markup (<i>, <sup>, MathML, ...) is flattened to plain text.
# xmltodict would otherwise split the text from the tags and lose the word order.
TEXT_ELEMENTS = ("ArticleTitle", "VernacularTitle", "AbstractText")


def flatten_inline_markup(content: bytes) -> bytes:
    """Replace child elements of text fields with their text, keeping attributes."""
    root = ET.fromstring(content)
    for tag in TEXT_ELEMENTS:
        for element in root.iter(tag):
            if len(element):
                text = "".join(element.itertext())
                for child in list(element):
                    element.remove(child)
                element.text = text
    return ET.tostring(root, encoding="utf-8")


NCBI_EUTILS_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


class PubMedClient:
    """E-utilities client.

    `base_url` defaults to $KIREN_EUTILS_URL or NCBI. `api_key` and `email` default to
    $NCBI_API_KEY and $NCBI_EMAIL; NCBI allows 3 requests/s without a key, 10 with one.
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        email: str | None = None,
        tool: str = "kiren",
    ):
        base_url = base_url or os.getenv("KIREN_EUTILS_URL") or NCBI_EUTILS_URL
        self.base_url = base_url.rstrip("/") + "/"
        self.api_key = api_key or os.getenv("NCBI_API_KEY")
        self.email = email or os.getenv("NCBI_EMAIL")
        self.tool = tool

    def _get(self, eutil: str, params: dict[str, Any]) -> bytes:
        params = {**params, "tool": self.tool}
        if self.email:
            params["email"] = self.email
        if self.api_key:
            params["api_key"] = self.api_key
        response = requests.get(f"{self.base_url}{eutil}", params=params, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.content

    def search(self, query: str, use_history: bool = False, retmax: int = 100) -> dict[str, Any]:
        """Search PubMed and return results.

        Args:
            query: The search query string
            use_history: If True, store results on NCBI server and return WebEnv and query_key
                         for subsequent operations
            retmax: Maximum number of results to return

        Returns:
            Dict with id_list, count, ret_max, ret_start, and webenv/query_key if use_history
        """
        eutil = "esearch.fcgi"
        params = {
            "db": "pubmed",
            "term": query,
            "usehistory": "y" if use_history else "n",
            "retmode": "xml",
            "retmax": retmax,
        }
        xml = xmltodict.parse(self._get(eutil, params))
        result = xml.get("eSearchResult", {})
        id_list = (result.get("IdList") or {}).get("Id", [])
        if isinstance(id_list, str):
            id_list = [id_list]
        elif not isinstance(id_list, list):
            id_list = []
        out = {
            "count": result.get("Count", "0"),
            "ret_max": result.get("RetMax", "0"),
            "ret_start": result.get("RetStart", "0"),
            "id_list": id_list,
        }
        if "WebEnv" in result:
            out["webenv"] = result["WebEnv"]
        if "QueryKey" in result:
            out["query_key"] = result["QueryKey"]
        return out

    def fetch_details(
        self,
        id_list: list[str] | None = None,
        webenv: str | None = None,
        query_key: str | None = None,
        retmax: int = 100,
        retstart: int = 0,
    ) -> list[dict]:
        """Fetch article details for given IDs or from a previous search.

        Args:
            id_list: List of PubMed IDs to fetch details for
            webenv: WebEnv string from a previous search
            query_key: Query key from a previous search
            retmax: Maximum number of records to retrieve
            retstart: Index of first record to retrieve

        Returns:
            List of article details dictionaries. Returns empty list if no results found.
        """
        if not id_list and not (webenv and query_key):
            return []
        eutil = "efetch.fcgi"
        params = {"db": "pubmed", "retmode": "xml", "retmax": retmax, "retstart": retstart}
        if id_list:
            params["id"] = ",".join(str(i) for i in id_list)
        else:
            params["WebEnv"] = webenv
            params["query_key"] = query_key
        xml_dict = xmltodict.parse(flatten_inline_markup(self._get(eutil, params)))
        data = xml_dict.get("PubmedArticleSet") or {}
        articles = data.get("PubmedArticle", [])
        if not articles:
            return []
        if not isinstance(articles, list):
            return [articles]
        return articles

    def search_and_fetch(self, query: str, max_results: int = 100) -> list[dict]:
        """Convenience method to search and fetch details in one operation.

        Args:
            query: The search query string
            max_results: Maximum number of results to return

        Returns:
            List of article details dictionaries
        """
        search_results = self.search(query, use_history=True)
        if not search_results or int(search_results.get("count", 0)) == 0:
            return []
        webenv = search_results.get("webenv")
        query_key = search_results.get("query_key")
        if not webenv or not query_key:
            id_list = search_results.get("id_list", [])
            if not id_list:
                return []
            id_list = id_list[:max_results]
            return self.fetch_details(id_list=id_list)
        return self.fetch_details(webenv=webenv, query_key=query_key, retmax=max_results)
