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
            author_info = f"{author.get('ForeName', '')} {author.get('LastName', '')}".strip(
            )
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

    @staticmethod
    def _parse_formatted_text(text_data: dict | str) -> str:
        """Parse text with formatting elements (italics, bold, etc) into plain text."""
        if isinstance(text_data, str):
            return text_data
        if not isinstance(text_data, dict):
            return str(text_data)

        main_text = text_data.get('#text', '')

        # Handle formatted text tags
        for tag in ['i', 'b', 'sup', 'sub']:
            if tag in text_data:
                formatted_text = text_data[tag]
                # Handle both string and list cases
                if isinstance(formatted_text, list):
                    formatted_text = ' '.join(str(item) for item in formatted_text)
                elif not isinstance(formatted_text, str):
                    formatted_text = str(formatted_text)
                
                # Insert formatted text at start if main text starts with space
                # Otherwise append space between formatted and main text
                if main_text.startswith(' '):
                    main_text = formatted_text + main_text
                else:
                    main_text = formatted_text + ' ' + main_text

        return main_text.strip()

    @classmethod
    def parse_article_details(
            cls,
            detail: dict,
            convert_date: bool = False) -> Optional[ArticleDetails]:
        """Parse a single article's details into a clean dictionary."""
        if not detail or 'MedlineCitation' not in detail:
            return None

        article = detail['MedlineCitation'].get('Article', {})
        pmid = detail['MedlineCitation'].get('PMID', {}).get('#text', '')

        pub_date = cls._extract_publication_date(article)
        if convert_date:
            pub_date = convert_publication_date(pub_date)

        title = article.get('ArticleTitle', '')
        title = cls._parse_formatted_text(title)

        return {
            'title': title,
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
        return [cls.parse_article_details(detail)
                for detail in details if detail]
