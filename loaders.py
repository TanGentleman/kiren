import csv
import pandas as pd
from typing import List, Optional

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from typing import TypedDict, Union

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

def convert_publication_date(date_dict: dict) -> str:
    """Convert the publication date dictionary to a string."""
    if not date_dict:
        return ''
    if isinstance(date_dict, dict):
        return f"{date_dict['year']}-{date_dict['month']}-{date_dict['day']}"
    else:
        return str(date_dict)

def save_to_csv(data: List[ArticleDetails], filename: str = 'output.csv', fields: Optional[List[str]] = None) -> None:
    """Save list of dictionaries to CSV file.
    
    Args:
        data: List of dictionaries containing the data to save
        filename: Output CSV filename
        fields: Optional list of fields to include. If None, uses all fields from first item.
    
    Raises:
        ValueError: If data is empty or fields specified don't exist in data
    """
    if not data:
        raise ValueError("Data cannot be empty")
        
    if fields is None:
        fields = list(data[0].keys())
    else:
        # Validate fields exist in first item
        missing = set(fields) - set(data[0].keys())
        if missing:
            raise ValueError(f"Fields {missing} not found in data")
            
    with open(filename, 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=fields, extrasaction='ignore')
        dict_writer.writeheader()
        dict_writer.writerows(data)

def save_to_excel(data: List[ArticleDetails], filename: str = 'output.xlsx', fields: Optional[List[str]] = None) -> None:
    """Save list of dictionaries to Excel file.
    
    Args:
        data: List of dictionaries containing the data to save
        filename: Output Excel filename
        fields: Optional list of fields to include. If None, uses all fields from first item.
        
    Raises:
        ValueError: If data is empty or fields specified don't exist in data
    """
    if not data:
        raise ValueError("Data cannot be empty")
        
    if fields is not None:
        # Validate fields exist in first item
        missing = set(fields) - set(data[0].keys())
        if missing:
            raise ValueError(f"Fields {missing} not found in data")
        df = pd.DataFrame(data)[fields]
    else:
        df = pd.DataFrame(data)
        
    df.to_excel(filename, index=False)

def save_to_pdf(data: List[ArticleDetails], filename: str = 'output.pdf', fields: Optional[List[str]] = None) -> None:
    """Save list of dictionaries to a formatted PDF file.
    
    Args:
        data: List of dictionaries containing the data to save
        filename: Output PDF filename
        fields: Optional list of fields to include. If None, uses all fields from first item.
        
    Raises:
        ValueError: If data is empty or fields specified don't exist in data
    """
    if not data:
        raise ValueError("Data cannot be empty")
        
    if fields is None:
        fields = list(data[0].keys())
    else:
        # Validate fields exist in first item
        missing = set(fields) - set(data[0].keys()) 
        if missing:
            raise ValueError(f"Fields {missing} not found in data")

    # Create PDF document
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=30, leftMargin=30)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Add each article as a separate section
    for item in data:
        # Add title 
        title_text = str(item.get('title', ''))  # Convert to string and handle missing title
        title = Paragraph(title_text, styles['Heading1'])
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Add authors
        if 'authors' in item and item['authors']:
            authors_text = f"Authors: {', '.join(str(a) for a in item['authors'])}"
            authors = Paragraph(authors_text, styles['Normal'])
            elements.append(authors)
            elements.append(Spacer(1, 12))
        
        # Add date if available
        if 'publication_date' in item and item['publication_date']:
            date_text = convert_publication_date(item['publication_date'])
            date = Paragraph(date_text, styles['Normal'])
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
