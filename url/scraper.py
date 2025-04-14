import requests
from bs4 import BeautifulSoup

def extract_paragraph_text(url: str) -> list[str]:
    """Return every <p> tag’s text (stripped) from *url*."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; ParagraphScraper/1.0; +https://github.com/you)"
        )
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()                # 4xx/5xx → exception

    soup = BeautifulSoup(resp.text, "lxml")  # fast C‑based parser
    p_text = [p.get_text(strip=True) for p in soup.find_all("p")]
    return [p.replace(r"\n", " ") for p in p_text]

def scrape_paragraphs(url: str) -> list[str]:
    import requests, re
    from bs4 import BeautifulSoup

    html = requests.get(url, timeout=10).text
    soup = BeautifulSoup(html, "lxml")
    return [
        re.sub(r"\s+", " ", p.get_text()).strip()
        for p in soup.select("p")
        if p.get_text(strip=True)      # skip completely empty <p>
    ]



if __name__ == "__main__":
    print(scrape_paragraphs("https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ApplicationEngineOverview.html?pli=ul_d328e35_tape"))