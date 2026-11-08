import csv
import os

import pytest
from conftest import RECORDED_TERM

from pubmed_tools import cli


@pytest.fixture
def eutils(fake_eutils, monkeypatch):
    base_url, state = fake_eutils
    monkeypatch.setenv("KIREN_EUTILS_URL", base_url)
    return state


def _run(args):
    with pytest.raises(SystemExit) as exit_info:
        cli.run(args)
    return exit_info.value.code


def test_cli_exports_all_formats(eutils, tmp_path):
    out = tmp_path / "out"
    assert _run([RECORDED_TERM, "--all", "--out", str(out)]) == 0
    assert sorted(os.listdir(out)) == ["output.csv", "output.pdf", "output.xlsx"]
    with open(out / "output.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert [r["pmid"] for r in rows] == ["38860195", "38798998", "42344625"]
    assert rows[0]["publication_date"] == "2023-09-30"
    assert rows[0]["authors"].startswith("Nazanin Naseri-Karimi; Hassan Vatandoost")


def test_cli_without_results_writes_nothing(eutils, tmp_path):
    assert _run(["zzxqvnonexistentterm123", "--csv", "--out", str(tmp_path)]) == 0
    assert os.listdir(tmp_path) == []


def test_cli_requires_a_format(capsys):
    assert _run(["drosophila"]) == 2
    assert "--csv" in capsys.readouterr().err


def test_cli_exits_nonzero_when_pubmed_fails(eutils, tmp_path):
    eutils.fail_with = 503
    assert _run([RECORDED_TERM, "--csv", "--out", str(tmp_path)]) == 1
    assert os.listdir(tmp_path) == []


def test_cli_exits_1_when_an_export_fails(eutils, tmp_path):
    not_a_dir = tmp_path / "file"
    not_a_dir.write_text("")
    assert _run([RECORDED_TERM, "--csv", "--out", str(not_a_dir)]) == 1
