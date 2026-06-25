from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from pydantic import BaseModel
from tools import search_tool, wiki_tool


load_dotenv()

llm = ChatOpenAI(model="gpt-oss-120b")
tools = [search_tool, wiki_tool]
class ResearchResponse(BaseModel):
    topic: str
    summary: str
    sources: list[str]
    tools_used: list[str]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=(
        "You are a research assistant that will help generate a research paper. "
        "Answer the user query and use necessary tools. "
        "Return a response that matches the required schema."
    ),
    response_format=ResearchResponse,
)
query = input("What's the question? ")
result = agent.invoke({"messages": [{"role": "user", "content": query}]})

try:
    structured_response = result["structured_response"]
    print(structured_response)
except Exception as e:
    print("Error parsing response", e, "Raw Response - ", result)







