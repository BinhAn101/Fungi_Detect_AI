from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from pydantic import BaseModel
from tools import search_tool, wiki_tool
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
from vector import retriever

llm = ChatOpenAI(model="gpt-oss-120b")

template = """
Bạn là một trợ lý AI. Nhiệm vụ của bạn là trả lời câu hỏi CHỈ DỰA VÀO thông tin được cung cấp dưới đây.
Nếu thông tin dưới đây không chứa câu trả lời, hãy nói "Tôi không tìm thấy thông tin trong dữ liệu được cung cấp." Không tự bịa ra câu trả lời.

Thông tin cung cấp:
{info}

Câu hỏi: {question}
"""
prompt = ChatPromptTemplate.from_template(template)
chain = prompt | llm

while True:
    print("-------------------------------")
    question = input("Bạn muốn hỏi gì? (bấm q để thoát): ")
    if question == "q":
        break

    docs = retriever.invoke(question)
    info_text = "\n\n".join([doc.page_content for doc in docs])
    
    result = chain.invoke({"info": info_text, "question": question})
    print(result.content)
