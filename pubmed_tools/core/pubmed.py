from pubmed_sdk import PubMed

class PubMed:
    """Base PubMed client class."""
    
    def search(self, query: str):
        """Search PubMed and return results."""
        raise NotImplementedError
        
    def fetch_details(self, id_list):
        """Fetch article details for given IDs."""
        raise NotImplementedError 