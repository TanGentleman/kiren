import pytest
import requests
from conftest import RECORDED_TERM

from pubmed_tools.core.client import PubMedClient
from pubmed_tools.parsers.article import ArticleParser


@pytest.fixture
def client(fake_eutils, monkeypatch):
    monkeypatch.delenv("NCBI_API_KEY", raising=False)
    monkeypatch.delenv("NCBI_EMAIL", raising=False)
    base_url, _ = fake_eutils
    return PubMedClient(base_url=base_url)


def test_search(client, fake_eutils):
    result = client.search(RECORDED_TERM, use_history=True)
    assert result["id_list"] == ["42344625", "38860195", "38798998"]
    assert result["count"] == "3"
    assert result["webenv"].startswith("MCID_")
    assert result["query_key"] == "1"
    path, params = fake_eutils[1].requests[-1]
    assert path == "/entrez/eutils/esearch.fcgi"
    assert params["db"] == "pubmed"
    assert params["usehistory"] == "y"
    assert params["tool"] == "kiren"
    assert "api_key" not in params


def test_search_without_results(client):
    result = client.search("zzxqvnonexistentterm123")
    assert result["count"] == "0"
    assert result["id_list"] == []


def test_fetch_details_by_id(client):
    details = client.fetch_details(["38798998", "38860195"])
    pmids = [d["MedlineCitation"]["PMID"]["#text"] for d in details]
    assert pmids == ["38860195", "38798998"]


def test_fetch_details_unknown_id(client):
    assert client.fetch_details(["99999999999"]) == []


def test_fetch_details_without_ids_makes_no_request(client, fake_eutils):
    assert client.fetch_details([]) == []
    assert fake_eutils[1].requests == []


def test_search_and_fetch_uses_history(client, fake_eutils):
    articles = ArticleParser.parse_all_details(client.search_and_fetch(RECORDED_TERM))
    assert [a["pmid"] for a in articles] == ["38860195", "38798998", "42344625"]
    path, params = fake_eutils[1].requests[-1]
    assert path.endswith("/efetch.fcgi")
    assert params["WebEnv"].startswith("MCID_")
    assert "id" not in params


def test_search_and_fetch_without_results(client, fake_eutils):
    assert client.search_and_fetch("zzxqvnonexistentterm123") == []
    assert len(fake_eutils[1].requests) == 1


def test_parsed_text_keeps_inline_markup_words(client):
    first, second, third = ArticleParser.parse_all_details(
        client.fetch_details(["38860195", "38798998", "42344625"])
    )
    assert first["title"] == (
        "Drosophila melanogaster Laboratory Rearing for Wolbachia-Based Control "
        "Programs, a Component of Dengue Control."
    )
    assert first["abstract"].startswith(
        "BACKGROUND: Drosophila melanogaster flies are smooth, low upkeep and safe"
    )
    assert (
        "requirements were provided for laboratory rearing of D. melanogaster."
        in (first["abstract"])
    )
    assert first["publication_date"] == {"year": "2023", "month": "09", "day": "30"}
    assert second["title"].startswith(
        "The genome sequence of a drosophilid fruit fly, Drosophila funebris (Fabricius"
    )
    assert "Tree of Life Core Informatics collective" in second["authors"]
    assert "" not in second["authors"]
    assert "<" in third["abstract"]


def test_api_key_and_email_from_environment(fake_eutils, monkeypatch):
    base_url, state = fake_eutils
    monkeypatch.setenv("KIREN_EUTILS_URL", base_url)
    monkeypatch.setenv("NCBI_API_KEY", "test-key")
    monkeypatch.setenv("NCBI_EMAIL", "me@example.org")
    PubMedClient().search("anything")
    _, params = state.requests[-1]
    assert params["api_key"] == "test-key"
    assert params["email"] == "me@example.org"


def test_http_errors_raise(client, fake_eutils):
    fake_eutils[1].fail_with = 500
    with pytest.raises(requests.HTTPError):
        client.search(RECORDED_TERM)
    with pytest.raises(requests.HTTPError):
        client.fetch_details(["38860195"])


def test_expired_history_raises(client):
    with pytest.raises(requests.HTTPError):
        client.fetch_details(webenv="MCID_expired", query_key="1")


def test_core_star_import():
    namespace = {}
    exec("from pubmed_tools.core import *", namespace)
    assert "PubMedClient" in namespace
