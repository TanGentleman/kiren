from typing import List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from .base import BaseExporter
from ..core.models import ArticleDetails
from ..parsers.date import convert_publication_date

class PDFExporter(BaseExporter):
    def export(self, data: List[ArticleDetails], filename: str = 'output.pdf', fields: Optional[List[str]] = None) -> None:
        """Export data to formatted PDF file."""
        fields = self._validate_data(data, fields)
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=30, leftMargin=30)
        elements = []
        styles = getSampleStyleSheet()
        
        # Add each article as a separate section
        for item in data:
            # Add title
            title = Paragraph(str(item.get('title', '')), styles['Heading1'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Add authors
            if 'authors' in item and item['authors']:
                authors_text = f"Authors: {', '.join(str(a) for a in item['authors'])}"
                authors = Paragraph(authors_text, styles['Normal'])
                elements.append(authors)
                elements.append(Spacer(1, 12))
            
            # Add date
            if 'publication_date' in item and item['publication_date']:
                date_text = convert_publication_date(item['publication_date'])
                date = Paragraph(f"Published: {date_text}", styles['Normal'])
                elements.append(date)
                elements.append(Spacer(1, 12))
            
            # Add PMID with URL
            if 'pmid' in item and item['pmid']:
                pmid_url = f"https://pubmed.ncbi.nlm.nih.gov/{item['pmid']}/"
                pmid_text = f"PMID: {item['pmid']} ({pmid_url})"
                pmid = Paragraph(pmid_text, styles['Normal'])
                elements.append(pmid)
                elements.append(Spacer(1, 12))
                
            # Add abstract
            if 'abstract' in item and item['abstract']:
                abstract_text = f"Abstract: {str(item['abstract'])}"
                abstract = Paragraph(abstract_text, styles['Normal'])
                elements.append(abstract)
            
            elements.append(PageBreak())
            
        doc.build(elements) 