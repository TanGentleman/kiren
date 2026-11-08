import os

import pytest
import requests
from unittest.mock import patch, Mock
from pubmed_tools.core.client import PubMedClient
from pubmed_tools.parsers.article import ArticleParser

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


def test_core_star_import():
    namespace = {}
    exec("from pubmed_tools.core import *", namespace)
    assert "PubMedClient" in namespace


FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def _fixture(name: str) -> str:
    with open(os.path.join(FIXTURES, name), encoding="utf-8") as f:
        return f.read()


def test_fetch_details_keeps_text_around_inline_markup(client):
    with patch("requests.get") as mock_get:
        mock_get.return_value = _make_response(_fixture("efetch.xml"))
        articles = ArticleParser.parse_all_details(client.fetch_details(["38860195"]))
    first = articles[0]
    assert first["title"] == (
        "Drosophila melanogaster Laboratory Rearing for Wolbachia-Based Control "
        "Programs, a Component of Dengue Control."
    )
    assert first["abstract"].startswith(
        "BACKGROUND: Drosophila melanogaster flies are smooth, low upkeep and safe")
    assert "requirements were provided for laboratory rearing of D. melanogaster." in first["abstract"]


def test_fetch_details_raises_on_http_error(client):
    response = _make_response("", status_code=500)
    response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
    with patch("requests.get", return_value=response):
        with pytest.raises(requests.HTTPError):
            client.fetch_details(["123"])
