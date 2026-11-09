import socket

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from pubmed_tools.web import app  # noqa: E402

client = TestClient(app)


def test_index_serves_the_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Paper Metadata" in response.text


def closed_port_url() -> str:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return f"http://127.0.0.1:{sock.getsockname()[1]}"


@pytest.mark.parametrize(
    "doi, status",
    [
        ("https://doi.org/10.1093/scan/nsq093", 200),
        ("https://doi.org/10.0000/does-not-exist", 404),
    ],
)
def test_get_status(fake_openalex, doi, status):
    response = client.get("/get", params={"url": doi})
    assert response.status_code == status
    if status == 200:
        assert response.json()["title"] == "Neural substrates underlying intentional empathy"


def test_get_is_502_when_openalex_is_unreachable(monkeypatch):
    monkeypatch.setenv("KIREN_OPENALEX_URL", closed_port_url())
    response = client.get("/get", params={"url": "https://doi.org/10.1093/scan/nsq093"})
    assert response.status_code == 502
    assert response.json()["detail"].startswith("OpenAlex request failed")
