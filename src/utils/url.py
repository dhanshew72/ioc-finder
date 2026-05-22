import hashlib
import urllib


def read_url(url: str):
    """
    Reads a single url and returns the content
    url: str url to read
    :return: content of url
    """
    with urllib.request.urlopen(url) as response:
        url_bytes = response.read()
        return url_bytes

def hash_url(url: str):
    """
    Reads a single url and returns the hashed content
    :param url: str url to hash
    :return: hashed url
    """
    return hashlib.sha256(url.encode()).hexdigest()
