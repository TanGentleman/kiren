import pytest
from unittest.mock import patch, Mock
from pubmed_tools.core.client import PubMedClient

@pytest.fixture
def client():
    return PubMedClient()

def _make_response(content: str, status_code: int = 200):
    mock_resp = Mock()
    mock_resp.content = content.encode("utf-8")
    mock_resp.status_code = status_code
    mock_resp.raise_for_status = Mock()
    return mock_resp

def test_search(client):
    # Arrange
    xml = """
    <eSearchResult>
        <Count>2</Count>
        <RetMax>2</RetMax>
        <RetStart>0</RetStart>
        <IdList>
            <Id>123</Id>
            <Id>456</Id>
        </IdList>
        <WebEnv>webenv123</WebEnv>
        <QueryKey>1</QueryKey>
    </eSearchResult>
    """
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_response(xml)
        # Act
        result = client.search("test query")
        # Assert
        assert result["id_list"] == ["123", "456"]
        assert result["count"] == "2"
        assert result["webenv"] == "webenv123"
        assert result["query_key"] == "1"
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "esearch.fcgi" in args[0]
        assert kwargs["params"]["term"] == "test query"

def test_fetch_details(client):
    # Arrange
    xml = """
    <PubmedArticleSet>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>123</PMID>
            </MedlineCitation>
        </PubmedArticle>
        <PubmedArticle>
            <MedlineCitation>
                <PMID>456</PMID>
            </MedlineCitation>
        </PubmedArticle>
    </PubmedArticleSet>
    """
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_response(xml)
        # Act
        result = client.fetch_details(["123", "456"])
        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["MedlineCitation"]["PMID"] == "123"
        assert result[1]["MedlineCitation"]["PMID"] == "456"
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "efetch.fcgi" in args[0]
        assert "123,456" in kwargs["params"]["id"]
