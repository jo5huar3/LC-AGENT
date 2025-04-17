import requests, bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class SubjectScraper:
    def __init__(self, base_url: str):
        """
        :param base_url: The URL of the page containing your <a> tags
        """
        self.base_url = base_url
        self.tagPool = []
        self.urlPool = []

    def setTagPool(self, subject: str, criteria: str = ""):
        html  = requests.get(self.base_url).text
        soup  = bs4.BeautifulSoup(html, "lxml") 
        allTags = soup.select(criteria)
        self.tagPool = [tag for tag in allTags if tag.get_text(strip=True) in subject ]
        self.urlPool = [urljoin(self.base_url, tag.find("a")["href"]) for tag in self.tagPool]
        
        for url in self.urlPool:
            html  = requests.get(url).text
            soup  = bs4.BeautifulSoup(html, "lxml") 
            print(soup)



    def get_links(self) -> list[tuple[str, str]]:
        """
        Fetch base_url, parse all <a> tags, and return list of (link_text, absolute_url).
        """
        resp = requests.get(self.base_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        links = []
        for a in soup.select('li.treeParent a'):
            text = a.get_text(strip=True)
            href = a.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                links.append((text, full_url))
        return links

    def scrape_by_subject(self, subject: str):
        """
        For each link whose text contains `subject`, visit and scrape.
        """
        for link_text, url in self.get_links():
            if subject.lower() in link_text.lower():
                print(f"→ Found subject '{link_text}', visiting {url}")
                self._scrape_page(url)

    def _scrape_page(self, url: str):
        """
        Fetch `url` and extract whatever you need from it.
        Example: pull all <h1> and <p> text.
        """
        resp = requests.get(url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')

        # Example extractions:
        title = soup.find('h1')
        paragraphs = soup.find_all('p')

        print("Page title:", title.get_text(strip=True) if title else "(no H1)")
        for p in paragraphs:
            print(" -", p.get_text(strip=True))
        print("-" * 40)

if __name__ == '__main__':
    # 1) Set your starting page here
    START_URL = 'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/index.html?focusnode=home'
    scraper = SubjectScraper(START_URL)

    scraper.setTagPool("Application Engine", "li.treeParent")
    # 2) Choose the subject you care about
    #scraper.scrape_by_subject("PeopleTools Overview")
