from typing import List, Optional
from ..core.models import ArticleDetails
from .date import convert_publication_date

class ArticleParser:
    @staticmethod
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

    @staticmethod
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

    @classmethod
    def parse_article_details(cls, detail: dict, convert_date: bool = False) -> Optional[ArticleDetails]:
        """Parse a single article's details into a clean dictionary."""
        if not detail or 'MedlineCitation' not in detail:
            return None
        
        article = detail['MedlineCitation'].get('Article', {})
        pmid = detail['MedlineCitation'].get('PMID', {}).get('#text', '')
        
        pub_date = cls._extract_publication_date(article)
        if convert_date:
            pub_date = convert_publication_date(pub_date)
            
        return {
            'title': article.get('ArticleTitle', ''),
            'abstract': cls.parse_abstract(article.get('Abstract', {})),
            'authors': cls.parse_authors(article.get('AuthorList', {})),
            'publication_date': pub_date,
            'pmid': pmid
        }

    @staticmethod
    def _extract_publication_date(article: dict) -> dict:
        """Extract publication date from article data."""
        date_sources = [
            article.get('ArticleDate'),
            article.get('Journal', {}).get('JournalIssue', {}).get('PubDate'),
            article.get('DateCompleted')
        ]
        
        for source in date_sources:
            if source:
                pub_date = {
                    'year': source.get('Year', ''),
                    'month': source.get('Month', ''),
                    'day': source.get('Day', '')
                }
                if any(pub_date.values()):
                    return pub_date
        
        return {'year': '', 'month': '', 'day': ''}

    @classmethod
    def parse_all_details(cls, details: List[dict]) -> List[ArticleDetails]:
        """Parse all articles in the details list."""
        return [cls.parse_article_details(detail) for detail in details if detail] 