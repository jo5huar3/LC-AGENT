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

    def setUrlPool(self, subject: str, root: str = "", leaf: str = ""):
        html  = requests.get(self.base_url).text
        soup  = bs4.BeautifulSoup(html, "lxml") 
        allTags = soup.select(root)
        self.tagPool = [tag for tag in allTags if tag.get_text(strip=True) in subject ]
        urlPool = [urljoin(self.base_url, tag.find("a")["href"]) for tag in self.tagPool]

        for url in urlPool:
            html  = requests.get(url).text
            soup  = bs4.BeautifulSoup(html, "lxml") 
            allTags = soup.select("a[href$='.html']")
            for tag in allTags:
                if len(tag.find_all()) > 1:
                    continue
                self.urlPool.append(  urljoin(self.base_url, tag["href"]) )
      
    def getUrls(self, max = -1):
        return self.urlPool if max < 0 else self.urlPool[:max]


    def printUrlPool(self):
        for url in self.urlPool:
            print(url)

if __name__ == '__main__':
    # 1) Set your starting page here
    START_URL = 'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/index.html?focusnode=home'
    scraper = SubjectScraper(START_URL)

    #scraper.setTagPool("Application Engine", "li.treeParent")
    scraper.setUrlPool("Application Engine",  "li.treeParent", "a.sbchild[href]")
    scraper.printUrlPool()

    print("\n\n\n", scraper.getUrls(5))