"""A fake E-utilities server that replays responses recorded from NCBI (fixtures/record.sh)."""

import os
import threading
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import pytest

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
RECORDED_TERM = "38860195[uid] OR 38798998[uid] OR 42344625[uid]"


def fixture_bytes(name: str) -> bytes:
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


def _recorded_webenv() -> str:
    return ET.fromstring(fixture_bytes("esearch.xml")).findtext("WebEnv")


def _efetch_ids(ids: list[str]) -> bytes:
    root = ET.fromstring(fixture_bytes("efetch.xml"))
    for article in list(root):
        if article.findtext("MedlineCitation/PMID") not in ids:
            root.remove(article)
    if not len(root):
        return fixture_bytes("efetch-empty.xml")
    return ET.tostring(root, encoding="utf-8")


class FakeEutils:
    def __init__(self):
        self.requests: list[tuple[str, dict[str, str]]] = []
        self.fail_with: int | None = None

    def respond(self, path: str, params: dict[str, str]) -> tuple[int, bytes]:
        self.requests.append((path, params))
        if self.fail_with:
            return self.fail_with, b"Internal Server Error"
        if path.endswith("/esearch.fcgi"):
            if params.get("term") == RECORDED_TERM:
                return 200, fixture_bytes("esearch.xml")
            return 200, fixture_bytes("esearch-empty.xml")
        if path.endswith("/efetch.fcgi"):
            if "id" in params:
                return 200, _efetch_ids(params["id"].split(","))
            if params.get("WebEnv") == _recorded_webenv() and params.get("query_key") == "1":
                return 200, fixture_bytes("efetch.xml")
            return 400, b"<eFetchResult><ERROR>Unable to obtain query #1</ERROR></eFetchResult>"
        return 404, b"not found"


@pytest.fixture
def fake_eutils():
    """Yields (base_url, FakeEutils); FakeEutils.requests logs every query string."""
    state = FakeEutils()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlparse(self.path)
            params = {k: v[0] for k, v in parse_qs(url.query).items()}
            status, body = state.respond(url.path, params)
            self.send_response(status)
            self.send_header("Content-Type", "text/xml; charset=UTF-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, args=(0.05,), daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/entrez/eutils/", state
    server.shutdown()
    server.server_close()
