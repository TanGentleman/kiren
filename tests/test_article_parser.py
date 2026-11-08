import pytest

from pubmed_tools.parsers.article import ArticleParser


@pytest.fixture
def parser():
    return ArticleParser()


def test_parse_authors_empty():
    assert ArticleParser.parse_authors({}) == []


def test_parse_authors_single():
    author_data = {"Author": {"ForeName": "John", "LastName": "Doe"}}
    assert ArticleParser.parse_authors(author_data) == ["John Doe"]


def test_parse_authors_multiple():
    author_data = {
        "Author": [
            {"ForeName": "John", "LastName": "Doe"},
            {"ForeName": "Jane", "LastName": "Smith"},
        ]
    }
    assert ArticleParser.parse_authors(author_data) == ["John Doe", "Jane Smith"]


def test_parse_abstract_empty():
    assert ArticleParser.parse_abstract({}) == ""


def test_parse_abstract_simple():
    abstract_data = {"AbstractText": "Test abstract"}
    assert ArticleParser.parse_abstract(abstract_data) == "Test abstract"


def test_parse_abstract_with_sections():
    abstract_data = {
        "AbstractText": [
            {"@Label": "BACKGROUND", "#text": "Test background"},
            {"@Label": "METHODS", "#text": "Test methods"},
        ]
    }
    expected = "BACKGROUND: Test background METHODS: Test methods"
    assert ArticleParser.parse_abstract(abstract_data) == expected


def test_parse_article_details(parser):
    article_data = {
        "MedlineCitation": {
            "PMID": {"#text": "12345"},
            "Article": {
                "ArticleTitle": "Test Title",
                "Abstract": {"AbstractText": "Test Abstract"},
                "AuthorList": {"Author": [{"ForeName": "John", "LastName": "Doe"}]},
                "Journal": {
                    "JournalIssue": {"PubDate": {"Year": "2023", "Month": "01", "Day": "01"}}
                },
            },
        }
    }

    result = parser.parse_article_details(article_data)

    assert result["title"] == "Test Title"
    assert result["abstract"] == "Test Abstract"
    assert result["authors"] == ["John Doe"]
    assert result["pmid"] == "12345"
    assert result["publication_date"] == {"year": "2023", "month": "01", "day": "01"}


def test_parse_authors_collective_name():
    author_data = {
        "Author": [
            {"ForeName": "John", "LastName": "Doe"},
            {"CollectiveName": "Tree of Life Core Informatics collective"},
        ]
    }
    assert ArticleParser.parse_authors(author_data) == [
        "John Doe",
        "Tree of Life Core Informatics collective",
    ]


def test_parse_article_details_pmid_without_attributes():
    detail = {"MedlineCitation": {"PMID": "123", "Article": {"ArticleTitle": "T"}}}
    assert ArticleParser.parse_article_details(detail)["pmid"] == "123"


def test_parse_all_details_skips_unparseable_records():
    details = [{"BookDocument": {}}, {"MedlineCitation": {"PMID": "1", "Article": {}}}]
    assert [a["pmid"] for a in ArticleParser.parse_all_details(details)] == ["1"]
