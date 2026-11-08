import pytest

from pubmed_tools.parsers.date import convert_publication_date


@pytest.mark.parametrize("date, expected", [
    ({'year': '2023', 'month': '09', 'day': '30'}, '2023-09-30'),
    ({'year': '2023', 'month': 'Sep', 'day': ''}, '2023-09'),
    ({'year': '2023', 'month': '5', 'day': '3'}, '2023-05-03'),
    ({'year': '2020', 'month': '', 'day': ''}, '2020'),
    ({'year': '', 'month': '', 'day': ''}, ''),
    ({}, ''),
    ('2023-01-01', '2023-01-01'),
])
def test_convert_publication_date(date, expected):
    assert convert_publication_date(date) == expected
