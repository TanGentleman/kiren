from pubmed_tools import PubMed
from typing import TypedDict, List, Union

DEFAULT_CONVERT_DATE = False

class ArticleDetails(TypedDict):
    """Schema for parsed article details.
    
    Fields:
        title: Article title as string
        abstract: Full abstract text as string
        authors: List of author names as strings
        publication_date: Defaults to dict with keys 'year', 'month', 'day'.
                           If convert_date=True, value is a string in the format YYYY-MM-DD
        pmid: PubMed ID as string
    """
    title: str
    abstract: str 
    authors: List[str]
    publication_date: Union[str, dict]
    pmid: str

def get_paper_ids(query: str, wrapper: PubMed = None):
    """Get the paper ids for a given query."""
    if wrapper is None:
        wrapper = PubMed()
    return wrapper.query(query)

def fetch_details(id_list, wrapper: PubMed = None):
    """Fetches the details of the articles in the id_list."""
    if wrapper is None:
        wrapper = PubMed()
    details = wrapper.fetch_details(id_list)
    return details.get('PubmedArticle')

def parse_authors(author_list) -> List[str]:
    """Extract author information from the AuthorList."""
    if not author_list:
        return []
    
    authors = author_list.get('Author', [])
    if not isinstance(authors, list):
        authors = [authors]
        
    parsed_authors = []
    for author in authors:
        author_info = f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip()
        parsed_authors.append(author_info)
    
    return parsed_authors

def parse_abstract(abstract: dict) -> str:
    """Extract and combine abstract sections."""
    if not abstract or 'AbstractText' not in abstract:
        return ''
    
    abstract_texts = abstract['AbstractText']
    if not isinstance(abstract_texts, list):
        abstract_texts = [abstract_texts]
    
    sections = []
    for text in abstract_texts:
        if isinstance(text, dict):
            label = text.get('@Label', '')
            content = text.get('#text', '')
            sections.append(f"{label}: {content}" if label else content)
        else:
            sections.append(str(text))
    
    return ' '.join(sections)

def parse_article_details(detail: dict, convert_date: bool = DEFAULT_CONVERT_DATE) -> ArticleDetails | None:
    """Parse a single article's details into a clean dictionary."""
    if not detail or 'MedlineCitation' not in detail:
        return None
    
    article = detail['MedlineCitation'].get('Article', {})
    pmid = detail['MedlineCitation'].get('PMID', {}).get('#text', '')
    
    # Get publication date from first available source
    pub_date = None
    date_sources = [
        article.get('ArticleDate'),
        article.get('Journal', {}).get('JournalIssue', {}).get('PubDate'),
        detail['MedlineCitation'].get('DateCompleted')
    ]
    
    for source in date_sources:
        if source:
            pub_date = {
                'year': source.get('Year', ''),
                'month': source.get('Month', ''),
                'day': source.get('Day', '')
            }
            if any(pub_date.values()):
                break
    
    if not pub_date:
        pub_date = {'year': '', 'month': '', 'day': ''}
        
    if convert_date:
        pub_date = convert_publication_date(pub_date)
        
    return {
        'title': article.get('ArticleTitle', ''),
        'abstract': parse_abstract(article.get('Abstract', {})),
        'authors': parse_authors(article.get('AuthorList', {})),
        'publication_date': pub_date,
        'pmid': pmid
    }

def convert_publication_date(date_dict: dict) -> str:
    """Convert the publication date dictionary to a string."""
    if not date_dict:
        return ''
    return f"{date_dict['year']}-{date_dict['month']}-{date_dict['day']}"

def parse_all_details(details) -> List[ArticleDetails]:
    """Parse all articles in the details list."""
    return [parse_article_details(detail) for detail in details if detail]

def print_articles(articles: List[ArticleDetails]):
    """Print all articles in the list."""
    for article in articles:
        print(article['title'])
        print(article['abstract'])
        print(article['authors'])
        print(article['publication_date'])
        print('\n\n')
