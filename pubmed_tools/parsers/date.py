MONTHS = {
    name: f"{i:02d}"
    for i, name in enumerate(
        ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"],
        start=1,
    )
}


def _two_digits(value: str) -> str:
    value = str(value or "").strip()
    if value.isdigit():
        return value.zfill(2)
    return MONTHS.get(value[:3].lower(), "")


def convert_publication_date(date_dict: dict) -> str:
    """Convert the publication date dictionary to YYYY, YYYY-MM or YYYY-MM-DD."""
    if not date_dict:
        return ""
    if isinstance(date_dict, dict):
        year = str(date_dict.get("year") or "").strip()
        month = _two_digits(date_dict.get("month"))
        day = _two_digits(date_dict.get("day")) if month else ""
        return "-".join(part for part in (year, month, day) if part)
    return str(date_dict)
