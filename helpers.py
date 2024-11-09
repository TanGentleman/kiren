from pubmed_sdk import PubMed

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

def parse_authors(author_list):
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

def parse_abstract(abstract):
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

def parse_article_details(detail):
    """Parse a single article's details into a clean dictionary."""
    if not detail or 'MedlineCitation' not in detail:
        return None
    
    article = detail['MedlineCitation'].get('Article', {})
    
    return {
        'title': article.get('ArticleTitle', ''),
        'abstract': parse_abstract(article.get('Abstract', {})),
        'authors': parse_authors(article.get('AuthorList', {})),
        'publication_date': {
            'year': article.get('ArticleDate', {}).get('Year', ''),
            'month': article.get('ArticleDate', {}).get('Month', ''),
            'day': article.get('ArticleDate', {}).get('Day', '')
        },
    }

def parse_all_details(details):
    """Parse all articles in the details list."""
    return [parse_article_details(detail) for detail in details if detail]

# Example usage:
# parsed_articles = parse_all_details(details)
# for article in parsed_articles:
#     print(f"Title: {article['title']}")
#     print(f"Authors: {', '.join(author['name'] for author in article['authors'])}")
#     print(f"Abstract: {article['abstract'][:200]}...")
#     print("\n")
