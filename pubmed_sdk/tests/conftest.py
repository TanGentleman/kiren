import pytest
from typing import List, Dict, Any

@pytest.fixture
def sample_pubmed_response() -> Dict[str, Any]:
    return {
        "count": "2",
        "id_list": ["12345", "67890"],
        "translation_set": [],
        "warning": "",
        "query_translation": "test[All Fields]"
    }

@pytest.fixture
def sample_article_details() -> List[Dict[str, Any]]:
    return [
        {
            'MedlineCitation': {
                'PMID': {'#text': '12345'},
                'Article': {
                    'ArticleTitle': 'Test Title',
                    'Abstract': {'AbstractText': 'Test Abstract'},
                    'AuthorList': {
                        'Author': [
                            {'ForeName': 'John', 'LastName': 'Doe'}
                        ]
                    },
                    'Journal': {
                        'JournalIssue': {
                            'PubDate': {
                                'Year': '2023',
                                'Month': '01',
                                'Day': '01'
                            }
                        }
                    }
                }
            }
        }
    ] 