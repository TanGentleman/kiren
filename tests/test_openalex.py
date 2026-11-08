import json

import pytest

from pubmed_tools import openalex

DOI_URL = "https://doi.org/10.1093/scan/nsq093"


def test_fetch_paper_metadata(fake_openalex):
    meta = openalex.fetch_paper_metadata(DOI_URL)
    assert meta["title"] == "Neural substrates underlying intentional empathy"
    assert meta["publication_date"] == "2011-04-21"
    assert meta["authors"][:2] == ["Moritz de Greck", "Gang Wang"]
    assert "anterior insula" in meta["keywords"]
    assert meta["cited_by_count"] == 76
    assert meta["abstract"].startswith("Although empathic responses to stimuli with emotional")
    assert meta["url"] == DOI_URL
    assert fake_openalex == ["/works/https://doi.org/10.1093/scan/nsq093"]


def test_unknown_doi_raises_not_found(fake_openalex):
    with pytest.raises(openalex.PaperNotFound):
        openalex.fetch_paper_metadata("https://doi.org/10.0000/does-not-exist")


def test_reconstruct_abstract_orders_words():
    assert openalex.reconstruct_abstract({"world": [1], "hello": [0, 2]}) == "hello world hello"
    assert openalex.reconstruct_abstract({}) is None
    assert openalex.reconstruct_abstract(None) is None


def test_keywords_fall_back_to_concepts():
    assert openalex.get_keywords({"concepts": [{"display_name": "Memory"}]}) == ["Memory"]


def test_kiren_doi_prints_json(fake_openalex, capsys):
    openalex.run([DOI_URL])
    assert json.loads(capsys.readouterr().out)["cited_by_count"] == 76


def test_kiren_doi_exits_1_when_not_found(fake_openalex, capsys):
    with pytest.raises(SystemExit) as exit_info:
        openalex.run(["https://doi.org/10.0000/does-not-exist"])
    assert exit_info.value.code == 1
    assert "no work" in capsys.readouterr().err
