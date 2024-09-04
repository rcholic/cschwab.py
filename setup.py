from setuptools import setup

with open("README.md") as file:
    long_description = file.read()

setup(
    name="CSchwabPy",
    version="0.1.4.2",
    description="Charles Schwab Stock & Option Trade API Client for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Tony W",
    author_email="ivytony@gmail.com",
    url="https://pypi.org/project/CSchwabPy/",
    keywords=["python", "CSchwabPy", "Charles Schwab", "Stock", "Option", "Trade"],
)
