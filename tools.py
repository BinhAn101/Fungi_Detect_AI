from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import Tool
from datetime import datetime

search = DuckDuckGoSearchRun()
def search_web(query: str) -> str:
    return search.run(query)

search_tool = Tool(
    name="search_web",
    func=search_web,
    description="Search the web for information",
)

wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(wiki_client=DuckDuckGoSearchRun(),top_k_results=1,doc_content_chars_max=100))