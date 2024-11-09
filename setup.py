from setuptools import setup, find_packages

setup(
    name="pubmed_tools",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pubmed_sdk',
        'xmltodict',
        'pandas',
        'reportlab',
        'openpyxl'
    ],
)