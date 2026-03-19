import requests


def fetch_remote(url: str) -> str:
    response = requests.get(url, timeout=3)
    return response.text[:200]
