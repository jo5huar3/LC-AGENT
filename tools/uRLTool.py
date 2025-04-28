from pydantic import BaseModel, Field
from langchain_core.tools import tool
from tools.url.scraper import WebScraper
from typing import List
from langchain_core.tools import StructuredTool

scraper = WebScraper()

class UrlExtractor(BaseModel):
    url: str = Field(description="""\
        Base url where to search and extract related urls.\
        """)
    subject: str = Field(description="""\
        Criteria used to qualify a url as being related.\
        """)
    root: str = Field(description="""\
        HTML element whose subtree will be searched for urls.\
        """)
    leaf: str = Field(description="""\
        HTML element that will contain the url to extract.\
        """)

@tool("url-extractor", args_schema=UrlExtractor, return_direct=False)
def extractUrlContent(url: str, subject: str, root: str, leaf: str) -> List[str]:
    """\
        From a base url, search the subtree of all qualified elements and \
        return the text content of those urls, that are related to the specified subject and \
        contained in the desired child element.\
    """
    scraper.setBaseUrl(url)
    scraper.setUrlPool(subject, root, leaf)
    return scraper.extractTextContent(10)


if __name__ == "__main__":
    print(extractUrlContent.invoke({
        "url" :'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/index.html?focusnode=home',
        "subject": "Application Engine",
        "root": "li.treeParent",
        "leaf": "a.sbchild[href]",
    }))

