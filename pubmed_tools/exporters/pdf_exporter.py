from typing import List, Optional, Dict
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

from .base import BaseExporter
from ..core.models import ArticleDetails
from ..parsers.date import convert_publication_date

logger = logging.getLogger(__name__)

class PDFExporter(BaseExporter):
    """PDF exporter for PubMed articles."""
    
    def __init__(self) -> None:
        self._register_fonts()
        self.styles = self._initialize_styles()

    def _register_fonts(self) -> None:
        """Register a Unicode-compatible font for use in the PDF."""
        pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
        addMapping('DejaVuSans', 0, 0, 'DejaVuSans')  # Can map Regular if needed

    def _initialize_styles(self) -> Dict[str, ParagraphStyle]:
        """Initialize custom paragraph styles for PDF export."""
        base_styles = getSampleStyleSheet()
        styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Heading1'],
                fontName='DejaVuSans',
            ),
            'body': ParagraphStyle(
                'CustomBody',
                parent=base_styles['Normal'],
                fontName='DejaVuSans',
            ),
        }
        return styles
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize and prepare text for PDF export."""
        if not text:
            return ""
        # The font change should handle the previously problematic characters
        return text
    
    def export(self, 
               data: List[ArticleDetails], 
               filename: str = 'output.pdf', 
               fields: Optional[List[str]] = None) -> None:
        """Export data to formatted PDF file."""
        try:
            fields = self._validate_data(data, fields)
            output_path = self._get_output_path(filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=letter,
                rightMargin=30,
                leftMargin=30)
            elements = []

            # Add each article as a separate section
            for item in data:
                try:
                    elements.extend(self._format_article(item))
                except Exception as e:
                    logger.error(f"Failed to format article {item.get('pmid', 'unknown')}: {str(e)}")
                    continue
            
            # Build PDF
            try:
                doc.build(elements)
                logger.info(f"Successfully exported {len(data)} articles to {output_path}")
            except Exception as e:
                raise IOError(f"Failed to create PDF: {str(e)}")
                
        except Exception as e:
            logger.error(f"PDF export failed: {str(e)}")
            raise

    def _format_article(self, item: ArticleDetails) -> List:
        """Format a single article for PDF export."""
        elements = []
        
        # Add title
        if title := item.get('title'):
            safe_title = self._sanitize_text(title)
            elements.append(Paragraph(safe_title, self.styles['title']))
            elements.append(Spacer(1, 12))

        # Add authors
        if authors := item.get('authors'):
            safe_authors = [self._sanitize_text(str(a)) for a in authors]
            authors_text = f"Authors: {', '.join(safe_authors)}"
            elements.append(Paragraph(authors_text, self.styles['body']))
            elements.append(Spacer(1, 12))

        # Add date
        if 'publication_date' in item and item['publication_date']:
            date_text = self._sanitize_text(convert_publication_date(item['publication_date']))
            date = Paragraph(f"Published: {date_text}", self.styles['body'])
            elements.append(date)
            elements.append(Spacer(1, 12))

        # Add PMID with URL
        if 'pmid' in item and item['pmid']:
            pmid_url = f"https://pubmed.ncbi.nlm.nih.gov/{item['pmid']}/"
            pmid_text = f"PMID: {item['pmid']} ({pmid_url})"
            elements.append(Paragraph(self._sanitize_text(pmid_text), self.styles['body']))
            elements.append(Spacer(1, 12))

        # Add abstract
        if 'abstract' in item and item['abstract']:
            safe_abstract = self._sanitize_text(str(item['abstract']))
            abstract_text = f"Abstract: {safe_abstract}"
            abstract = Paragraph(abstract_text, self.styles['body'])
            elements.append(abstract)

        elements.append(PageBreak())
        return elements