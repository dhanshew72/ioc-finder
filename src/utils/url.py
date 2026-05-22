import urllib


def read_url(url: str):
    """
    Reads a single url and returns the content
    url: str url to read
    """
    with urllib.request.urlopen(url) as response:
        pdf_bytes = response.read()
        return pdf_bytes
