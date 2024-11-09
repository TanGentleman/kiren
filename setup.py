from setuptools import setup, find_packages

setup(
    name="pubmed_sdk",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'xmltodict',
        'pandas',
        'reportlab'
    ],
)