from __future__ import annotations

import time
from typing import Callable, Dict, List, Set
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

def is_link_relevant(link_text: str, link_href: str, subject: str) -> bool:
    """
    Basic example: we say a link is 'relevant' if the subject keyword
    appears in either the text or the href. Feel free to enhance
    (regex, synonyms, partial matches, data attributes, etc.).
    """
    subject_lower = subject.lower()
    return (
        subject_lower in link_text.lower() or
        subject_lower in link_href.lower()
    )


from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

def enqueue_application_engine_links(
    soup: BeautifulSoup,
    page_url: str,
    domain: str,
    subject: str,
    visited: set[str],
    queue: list[str],
) -> None:
    """
    Push onto *queue* every <a> whose ancestor is:
        <li class="treeParent"> … <span>Application Engine</span> … </li>
    Only same‑domain links are accepted and duplicates are ignored.
    """
    # 1) Find the specific <li> nodes we care about
    for li in soup.find_all("li", class_="treeParent"):
        span = li.find("span", string=lambda s: s and subject in s)
        if not span:
            continue                      # this <li> is NOT the one we want

        # 2) Inside that <li> collect all <a> tags
        for a in li.find_all("a", href=True):
            href_abs = urljoin(page_url, a["href"])
            if urlparse(href_abs).netloc.lower() == domain and href_abs not in visited:
                queue.append(href_abs)

def scrape_by_subject(
    base_url: str,
    subject: str,
    *,
    max_pages: int = 100,
    delay: float = 0.0,
    session: requests.Session | None = None,
    relevance_checker: Callable[[str, str, str], bool] = is_link_relevant
) -> Dict[str, List[str]]:
    """
    Recursively scrape text paragraphs from base_url and *only* follow
    <a> links that:
    
      1) Are on the *same domain* as base_url, AND
      2) Pass the `relevance_checker` test for the given `subject`.

    Parameters
    ----------
    base_url : str
        The page where crawling begins.
    subject : str
        Keyword or phrase used to decide if a link is relevant enough to follow.
    max_pages : int
        Hard stop so we do not keep crawling forever (defaults to 100).
    delay : float
        Seconds to sleep between requests (politeness throttle).
    session : requests.Session
        Optional requests session to keep cookies / connection pooling.
    relevance_checker : callable
        Function signature: (link_text, link_href, subject) -> bool

    Returns
    -------
    dict[str, list[str]]
        A dict of {url -> list_of_paragraph_texts}.
    """
    session = session or requests.Session()
    domain = urlparse(base_url).netloc.lower()

    visited: Set[str] = set()
    queue: List[str] = [base_url]
    scraped_data: Dict[str, List[str]] = {}

    while queue and len(visited) < max_pages:
        url = queue.pop()
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = session.get(url, timeout=10)
            if resp.status_code != 200:
                continue
            if "text/html" not in resp.headers.get("Content-Type", ""):
                # skip non-HTML resources
                continue
        except requests.RequestException:
            # skip on any request failure
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract paragraphs from this page
        paragraphs = [
            p.get_text(" ", strip=True) 
            for p in soup.find_all("p")
            if p.get_text(strip=True)
        ]
        scraped_data[url] = paragraphs

        # Find all relevant links
        for a in soup.find_all("a", href=True):
            link_text = a.get_text(strip=True)
            link_href = urljoin(url, a["href"])  # handle relative paths
            link_parsed = urlparse(link_href)

            # 1) must be same domain
            if link_parsed.netloc.lower() != domain:
                continue

            # 2) must pass the custom 'relevance_checker'
            if relevance_checker(link_text, link_href, subject):
                if link_href not in visited:
                    queue.append(link_href)

        if delay:
            time.sleep(delay)

    return scraped_data





if __name__ == "__main__":
    # Example usage:
    base = "https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ApplicationEngineOverview.html?pli=ul_d328e35_tape"
    # Suppose we only want to follow links that mention "Application Engine"
    subject = "Application Engine"

    # ... after you have 'soup', 'page_url', 'domain', 'visited', 'queue'
    enqueue_application_engine_links(
        soup=soup,
        page_url=url,
        domain=domain,
        subject=subject,
        visited=visited,
        queue=queue,
    )




'''
    data = scrape_by_subject(
        base_url=base,
        subject=subject,
        max_pages=50,
        delay=0.1
    )

    # Now 'data' is a dict of {url: [list_of_paragraph_texts]}.
    # We visited only those pages whose links matched our subject criterion.
    for page_url, paragraphs in data.items():
        print(page_url, "→ #paragraphs:", len(paragraphs))
        # ... do something with each page's paragraphs ...
'''