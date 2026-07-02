from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os
import pandas as pd

load_dotenv()

df = pd.read_csv("Test.csv")
embeddings = OpenAIEmbeddings(model="Vietnamese_Embedding", check_embedding_ctx_length=False)

db_location = "./chroma_langchain_db"
add_documents = not os.path.exists(db_location)

if add_documents:
    documents = []
    ids = []

    for i, row in df.iterrows():
        document = Document(
            page_content= row["Tag"] + row["Trả lời"],
            id = str(i)
        )
        ids.append(str(i))
        documents.append(document)

vector_store = Chroma(
    collection_name= "Tra_loi",
    persist_directory = db_location,
    embedding_function=embeddings,
)

if add_documents:
    vector_store.add_documents( documents= documents, ids=ids)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 1}
)
