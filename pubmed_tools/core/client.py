from typing import List, Dict, Any
from pubmed_sdk import PubMed


class PubMedClient:
    def __init__(self):
        self.client = PubMed()

    def search(self, query: str) -> Dict[str, Any]:
        """Search PubMed and return results."""
        return self.client.search(query)

    def fetch_details(self, id_list: List[str]) -> List[dict]:
        """Fetch article details for given IDs.
        
        Args:
            id_list: List of PubMed IDs to fetch details for
            
        Returns:
            List of article details dictionaries. Returns empty list if no results found.
        """
        details = self.client.fetch_details(id_list)
        if not details:
            return []
            
        articles = details.get('PubmedArticle', [])
        # Handle case where single article is returned
        if not isinstance(articles, list):
            # NOTE: Should this raise an error instead?
            return [articles]
        return articles
