import os
from unittest.mock import Mock, patch

import pytest

from pubmed_tools import cli

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

ESEARCH = b"""<eSearchResult><Count>3</Count><RetMax>3</RetMax><RetStart>0</RetStart>
<IdList><Id>38860195</Id><Id>38798998</Id><Id>42344625</Id></IdList></eSearchResult>"""


def _fake_get(url, params=None, timeout=None):
    response = Mock(status_code=200, raise_for_status=Mock())
    if url.endswith("esearch.fcgi"):
        response.content = ESEARCH
    else:
        with open(os.path.join(FIXTURES, "efetch.xml"), "rb") as f:
            response.content = f.read()
    return response


def test_cli_exports_all_formats(tmp_path):
    with patch("requests.get", side_effect=_fake_get):
        with pytest.raises(SystemExit) as exit_info:
            cli.run(["drosophila", "--all", "--out", str(tmp_path / "out")])
    assert exit_info.value.code == 0
    names = sorted(os.listdir(tmp_path / "out"))
    assert names == ["output.csv", "output.pdf", "output.xlsx"]


def test_cli_requires_a_format(capsys):
    with pytest.raises(SystemExit) as exit_info:
        cli.run(["drosophila"])
    assert exit_info.value.code == 2
    assert "--csv" in capsys.readouterr().err


def test_cli_exits_nonzero_when_pubmed_fails(tmp_path):
    with patch("requests.get", side_effect=OSError("network down")):
        with pytest.raises(SystemExit) as exit_info:
            cli.run(["drosophila", "--csv", "--out", str(tmp_path)])
    assert exit_info.value.code == 1
    assert os.listdir(tmp_path) == []
