from typing import List, Dict, Any
from pubmed_sdk import PubMed

class PubMedClient:
    def __init__(self):
        self.client = PubMed()

    def search(self, query: str) -> Dict[str, Any]:
        """Search PubMed and return results."""
        return self.client.search(query)

    def fetch_details(self, id_list: List[str]) -> List[dict]:
        """Fetch article details for given IDs."""
        details = self.client.fetch_details(id_list)
        return details.get('PubmedArticle', []) 