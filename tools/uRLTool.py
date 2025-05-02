from pydantic import BaseModel, Field
from langchain_core.tools import tool
from tools.url.scraper import WebScraper
from typing import List
from langchain_core.tools import StructuredTool
from typing import Annotated, List

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
def extractUrlMatches(url: str, subject: str, root: str, leaf: str) -> List[str]:
    """\
        From a base url, search the subtree of every tag in html document that is of type root for text content that matches subject. Return a list of the urls in the html elements with tag type of leaf \
        if that subtree is relavent to subject.\
    """
    scraper.setBaseUrl(url)
    scraper.buildUrlPool(subject, root, leaf)
    return scraper.getUrls(10)

@tool
def extractWebContent(
    urls: Annotated[List[str], "list of strings over which to scrape the web content of."],
) -> str:
    """\
        Extract the web content from every string in urls and return scraped text content as one string.\
    """
    return scraper.extractTextContFromList(urls)
    

if __name__ == "__main__":
    print(extractUrlMatches.invoke({
        "url" :'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/index.html?focusnode=home',
        "subject": "Application Engine",
        "root": "li.treeParent",
        "leaf": "a.sbchild[href]",
    }))
    print(extractWebContent.invoke({
        "urls": ['https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ApplicationEngineOverview.html',
                'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ApplicationEngineImplementation.html', 
                'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ApplicationEngineFundamentals-077260.html', 
                'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/Meta-SQL-07725f.html', 
                'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ApplicationEngineProgramElements-07725e.html', 
                'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ApplicationEngineProgramTypes-077254.html', 
                'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ViewingApplicationEnginePrograms-07724c.html', 
                'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/FilteringViewContents-077244.html', 
                'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/PrintingProgramandFlowDefinitions-077242.html', 
                'https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/CreatingOpeningandRenamingPrograms-077241.html']
    }))

