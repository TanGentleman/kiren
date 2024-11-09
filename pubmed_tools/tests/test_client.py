import pytest
from unittest.mock import Mock, patch
from pubmed_tools.core.client import PubMedClient


@pytest.fixture
def mock_pubmed():
    with patch('pubmed_tools.core.client.PubMed') as mock:
        yield mock


@pytest.fixture
def client(mock_pubmed):
    return PubMedClient()


def test_search(client, mock_pubmed):
    # Arrange
    expected = {"id_list": ["123", "456"]}
    mock_pubmed.return_value.search.return_value = expected

    # Act
    result = client.search("test query")

    # Assert
    assert result == expected
    mock_pubmed.return_value.search.assert_called_once_with("test query")


def test_fetch_details(client, mock_pubmed):
    # Arrange
    mock_response = {"PubmedArticle": [{"id": "123"}, {"id": "456"}]}
    mock_pubmed.return_value.fetch_details.return_value = mock_response

    # Act
    result = client.fetch_details(["123", "456"])

    # Assert
    assert result == [{"id": "123"}, {"id": "456"}]
    mock_pubmed.return_value.fetch_details.assert_called_once_with([
                                                                   "123", "456"])
