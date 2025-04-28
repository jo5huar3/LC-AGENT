import requests
from bs4 import BeautifulSoup

def extract_paragraphs(url: str) -> list[str]:
    """
    Fetches the given URL and returns a list of all paragraph texts.
    """
    resp = requests.get(url)
    resp.raise_for_status()       # make sure we got a 2xx response
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # find all <p> tags and strip their text
    paragraphs = [p.get_text() for p in soup.find_all("p")]
    return [p.replace("\n", " ") for p in paragraphs]

if __name__ == "__main__":
    URL = "https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/LocatingTraceFiles-077145.html"
    for idx, text in enumerate(extract_paragraphs(URL), start=1):
        print(f"{text}")
