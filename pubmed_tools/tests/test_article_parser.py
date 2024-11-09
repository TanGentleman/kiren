import pytest
from pubmed_tools.parsers.article import ArticleParser


@pytest.fixture
def parser():
    return ArticleParser()


def test_parse_authors_empty():
    assert ArticleParser.parse_authors({}) == []


def test_parse_authors_single():
    author_data = {
        'Author': {
            'ForeName': 'John',
            'LastName': 'Doe'
        }
    }
    assert ArticleParser.parse_authors(author_data) == ['John Doe']


def test_parse_authors_multiple():
    author_data = {
        'Author': [
            {'ForeName': 'John', 'LastName': 'Doe'},
            {'ForeName': 'Jane', 'LastName': 'Smith'}
        ]
    }
    assert ArticleParser.parse_authors(author_data) == [
        'John Doe', 'Jane Smith']


def test_parse_abstract_empty():
    assert ArticleParser.parse_abstract({}) == ''


def test_parse_abstract_simple():
    abstract_data = {
        'AbstractText': 'Test abstract'
    }
    assert ArticleParser.parse_abstract(abstract_data) == 'Test abstract'


def test_parse_abstract_with_sections():
    abstract_data = {
        'AbstractText': [
            {'@Label': 'BACKGROUND', '#text': 'Test background'},
            {'@Label': 'METHODS', '#text': 'Test methods'}
        ]
    }
    expected = 'BACKGROUND: Test background METHODS: Test methods'
    assert ArticleParser.parse_abstract(abstract_data) == expected


def test_parse_article_details(parser):
    article_data = {
        'MedlineCitation': {
            'PMID': {'#text': '12345'},
            'Article': {
                'ArticleTitle': 'Test Title',
                'Abstract': {'AbstractText': 'Test Abstract'},
                'AuthorList': {
                    'Author': [
                        {'ForeName': 'John', 'LastName': 'Doe'}
                    ]
                },
                'Journal': {
                    'JournalIssue': {
                        'PubDate': {
                            'Year': '2023',
                            'Month': '01',
                            'Day': '01'
                        }
                    }
                }
            }
        }
    }

    result = parser.parse_article_details(article_data)

    assert result['title'] == 'Test Title'
    assert result['abstract'] == 'Test Abstract'
    assert result['authors'] == ['John Doe']
    assert result['pmid'] == '12345'
    assert result['publication_date'] == {
        'year': '2023', 'month': '01', 'day': '01'}
