from typing import Any

import pytest


@pytest.fixture
def sample_pubmed_response() -> dict[str, Any]:
    return {
        "count": "2",
        "id_list": ["12345", "67890"],
        "translation_set": [],
        "warning": "",
        "query_translation": "test[All Fields]",
    }


@pytest.fixture
def sample_article_details() -> list[dict[str, Any]]:
    return [
        {
            "MedlineCitation": {
                "PMID": {"#text": "12345"},
                "Article": {
                    "ArticleTitle": "Test Title",
                    "Abstract": {"AbstractText": "Test Abstract"},
                    "AuthorList": {"Author": [{"ForeName": "John", "LastName": "Doe"}]},
                    "Journal": {
                        "JournalIssue": {"PubDate": {"Year": "2023", "Month": "01", "Day": "01"}}
                    },
                },
            }
        }
    ]
