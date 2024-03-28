from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredPDFLoader, OnlinePDFLoader, PyPDFLoader, TextLoader
import os
from dotenv import load_dotenv
from langchain_community.vectorstores import Pinecone as PinecineLangchain
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from typing import Any, Dict, List
from langchain.chains import ConversationalRetrievalChain
load_dotenv()

OPENAI_API_KEY = os.getenv("SECRET_KEY")
_pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


# * File embedding
def handle_file_embedding(file_path: str, index_name: str):
    files = os.listdir(file_path)
    print("files", files)

    for file in files:
        loader = PyPDFLoader(file_path + "/" + file)
        doc = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=600, chunk_overlap=50)
        documents = text_splitter.split_documents(doc)
        print(f"Number of documents: {len(documents)}")

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large", api_key=OPENAI_API_KEY)
        PinecineLangchain.from_documents(
            documents, embeddings, index_name=Index_name)
        print("File embedded successfully")


# * Start conversation
def start_conversation(query: str, chat_history: List[Dict[str, Any]] = []):
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", api_key=OPENAI_API_KEY)
    search = PinecineLangchain.from_existing_index(
        embedding=embeddings, index_name=Index_name)

    chat = ChatOpenAI(verbose=True, temperature=0,
                      api_key=OPENAI_API_KEY, model="gpt-4-0125-preview")

    chain = ConversationalRetrievalChain.from_llm(
        llm=chat, retriever=search.as_retriever(), return_source_documents=True)

    return chain.invoke({"question": query, "chat_history": chat_history})
