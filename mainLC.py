from langchain_core.tools import tool, StructuredTool
from typing import List
from url.scraper import SubjectScraper

@tool
def getWebContents(url: str) -> List[str]:
    """Get the text content from a web page url."""
    scraper = SubjectScraper(url)
    scraper.setUrlPool("Application Engine",  "li.treeParent", "a.sbchild[href]")
    return ["Hello World"]


webScraper = StructuredTool.from_function(
    func=getWebContents,
    name="Web Scraper",
    description="Get a list of the web content at a specific url",
    return_direct=False
    )

print(webScraper.invoke("https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/index.html?focusnode=home"))