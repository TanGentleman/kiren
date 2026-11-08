import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from pubmed_tools.web import app  # noqa: E402

client = TestClient(app)


def test_index_serves_the_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Paper Metadata" in response.text


def test_get_returns_metadata(fake_openalex):
    response = client.get("/get", params={"url": "https://doi.org/10.1093/scan/nsq093"})
    assert response.status_code == 200
    assert response.json()["title"] == "Neural substrates underlying intentional empathy"


def test_get_unknown_doi_is_404(fake_openalex):
    response = client.get("/get", params={"url": "https://doi.org/10.0000/does-not-exist"})
    assert response.status_code == 404
