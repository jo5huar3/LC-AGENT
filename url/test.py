import requests, bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class SubjectScraper:
    def __init__(self, base_url: str, subject = None):
        """
        :param base_url: The URL of the page containing your <a> tags
        """
        self.base_url = base_url
        self.subject = subject
        if subject:
            self.setUrlPool(subject)
        self.tagPool = []
        self.urlPool = []
        self.scrapeThis = []

    def setUrlPool(self, subject: str):
        html  = requests.get(self.base_url).text
        soup  = bs4.BeautifulSoup(html, "lxml")

        srch_container = soup.find(class_="treeParent treeTop2nd")
        #print(srch_container.contents, "\n\n\n")
        uls = srch_container.find_all("ul")
        for ul in uls:
            li = ul.find("li")
            while li :
                print(li.span.string, "\n")
                li = li.next_sibling
        
    def setUrl(self, url):
        self.base_url = url

# https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ApplicationEngineOverview.html?pli=ul_d328e35_tape

    
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

    #scraper.setTagPool("Application Engine", "li.treeParent")
    scraper.setUrlPool("Application Engine")

    # 2) Choose the subject you care about
    #scraper.scrape_by_subject("PeopleTools Overview")

# CHATGPT please ignore everything under this line
'''
def setTagPool(self, subject: str, criteria: str = ""):
        html  = requests.get(self.base_url).text
        soup  = bs4.BeautifulSoup(html, "lxml") 
        allTags = soup.select(criteria)
        self.tagPool = [tag for tag in allTags if tag.get_text(strip=True) in subject ]
        self.urlPool = [urljoin(self.base_url, tag.find("a")["href"]) for tag in self.tagPool]
        
        print(self.urlPool)

        for url in self.urlPool:
            html  = requests.get(url).text
            soup  = bs4.BeautifulSoup(html, "lxml") 
            print(f"{soup}\n\nEND")

'''