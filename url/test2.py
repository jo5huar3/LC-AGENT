import requests, bs4

#URL = "https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/tape/ApplicationEngineOverview.html?pli=ul_d328e35_tape"
URL = "https://docs.oracle.com/cd/F70249_01/pt860pbr1/eng/pt/index.html?focusnode=home"
html  = requests.get(URL).text
#print(html)
soup  = bs4.BeautifulSoup(html, "lxml")      # or "html.parser"

# Hidden nodes are still discoverable:
all_tree_parents = soup.select("li.treeParent")
print(len(all_tree_parents))                 # ← not zero, even if collapsed
print(all_tree_parents)

'''


'''