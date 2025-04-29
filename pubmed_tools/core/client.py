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

from typing import List, Dict, Any, Optional
import requests
import xmltodict


class PubMedClient:
    def __init__(self):
        self.base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'

    def search(self, query: str, use_history: bool = False) -> Dict[str, Any]:
        """Search PubMed and return results.
        
        Args:
            query: The search query string
            use_history: If True, store results on NCBI server and return WebEnv and query_key
                         for subsequent operations
        
        Returns:
            Dictionary containing search results, including id_list and optionally WebEnv and query_key
        """
        eutil = 'esearch.fcgi'
        params = {
            'db': 'pubmed',
            'term': query,
            'usehistory': 'y' if use_history else 'n',
            'retmode': 'xml'
        }
        response = requests.get(f"{self.base_url}{eutil}", params=params)
        response.raise_for_status()
        xml = xmltodict.parse(response.content)
        result = xml.get('eSearchResult', {})
        id_list = result.get('IdList', {}).get('Id', [])
        if isinstance(id_list, str):
            id_list = [id_list]
        elif not isinstance(id_list, list):
            id_list = []
        out = {
            'count': result.get('Count', '0'),
            'ret_max': result.get('RetMax', '0'),
            'ret_start': result.get('RetStart', '0'),
            'id_list': id_list,
        }
        if 'WebEnv' in result:
            out['webenv'] = result['WebEnv']
        if 'QueryKey' in result:
            out['query_key'] = result['QueryKey']
        return out

    def fetch_details(self, id_list: Optional[List[str]] = None, 
                     webenv: Optional[str] = None, 
                     query_key: Optional[str] = None,
                     retmax: int = 100,
                     retstart: int = 0) -> List[dict]:
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
        eutil = 'efetch.fcgi'
        params = {
            'db': 'pubmed',
            'retmode': 'xml',
            'retmax': retmax,
            'retstart': retstart
        }
        if id_list:
            params['id'] = ','.join(str(i) for i in id_list)
        else:
            params['WebEnv'] = webenv
            params['query_key'] = query_key
        response = requests.get(f"{self.base_url}{eutil}", params=params)
        if response.status_code != 200:
            return []
        xml_dict = xmltodict.parse(response.content)
        data = xml_dict.get('PubmedArticleSet', {})
        articles = data.get('PubmedArticle', [])
        if not articles:
            return []
        if not isinstance(articles, list):
            return [articles]
        return articles

    def search_and_fetch(self, query: str, max_results: int = 100) -> List[dict]:
        """Convenience method to search and fetch details in one operation.
        
        Args:
            query: The search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of article details dictionaries
        """
        search_results = self.search(query, use_history=True)
        if not search_results or int(search_results.get('count', 0)) == 0:
            return []
        webenv = search_results.get('webenv')
        query_key = search_results.get('query_key')
        if not webenv or not query_key:
            id_list = search_results.get('id_list', [])
            if not id_list:
                return []
            id_list = id_list[:max_results]
            return self.fetch_details(id_list=id_list)
        return self.fetch_details(webenv=webenv, query_key=query_key, retmax=max_results)
