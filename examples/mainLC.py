from langchain_core.tools import tool, StructuredTool
from langchain_openai import ChatOpenAI
from typing import List
from url.scraper import SubjectScraper
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage



def getUrls(url: str) -> List[str]:
    """Get the text content from a web page url."""
    scraper = SubjectScraper(url)
    scraper.setUrlPool("Application Engine",  "li.treeParent", "a.sbchild[href]")
    #return ["Hello World"]
    return scraper.getUrls()


webScraper = StructuredTool.from_function(
    func=getUrls,
    name="Web Scraper",
    description="Get a list of the urls that are related to a subject from a specific url.",
    return_direct=False
    )

#print(webScraper.invoke("https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/index.html?focusnode=home"))

from langchain_core.prompts import PromptTemplate
model = ChatOpenAI(model="gpt-4o")



while (prompt := input("Enter a prompt (q to quit): ")) != "q":
    response = model.invoke(prompt)
    print(response.content)