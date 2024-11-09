def convert_publication_date(date_dict: dict) -> str:
    """Convert the publication date dictionary to a string."""
    if not date_dict:
        return ''
    if isinstance(date_dict, dict):
        return f"{date_dict['year']}-{date_dict['month']}-{date_dict['day']}"
    return str(date_dict) 