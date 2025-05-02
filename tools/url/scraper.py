import requests, bs4
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class WebScraper:
    def __init__(self, base_url = None, parser = "lxml"):
        """
        :param base_url: The URL of the page containing your <a> tags
        """
        self.base_url = base_url
        self.tagPool = []
        self.urlPool = []
        self.parser = parser

    def setBaseUrl(self, base_url):
        self.base_url = base_url

    def getSoup(self, url: str) -> bs4.BeautifulSoup:
        html  = requests.get(url)
        html.raise_for_status()
        return bs4.BeautifulSoup(html.text, self.parser) 

    def buildUrlPool(self, subject: str, root: str = "", leaf: str = ""):
        soup  = self.getSoup(self.base_url)
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

    def extractTextContent(self, max = -1) -> str:
        textContent = ""
        for i, url in enumerate(self.urlPool):
            if max != -1 and i > max:
                break
            soup  = self.getSoup(url)
            heading = soup.find('h1').get_text()
            paragraphs = [p.get_text() for p in soup.find_all("p")]
            heading = heading.replace("\n", " ") 
            extractText = [p.replace("\n", " ") for p in paragraphs]
            extractText.insert(0, heading)
            textContent += f'{ i }. ' + "\n".join(extractText) + "\n"
        return textContent

    def printUrlPool(self):
        for url in self.urlPool:
            print(url)

if __name__ == '__main__':
    # 1) Set your starting page here
    START_URL = 'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/index.html?focusnode=home'
    scraper = WebScraper()
    scraper.setBaseUrl(START_URL)
    #scraper.setTagPool("Application Engine", "li.treeParent")
    scraper.buildUrlPool("Application Engine",  "li.treeParent", "a.sbchild[href]")
    #scraper.printUrlPool()
    print("\n\n\n", scraper.getUrls(1))
    print(scraper.extractTextContent())