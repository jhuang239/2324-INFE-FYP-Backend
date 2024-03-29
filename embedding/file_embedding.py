from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, PyPDFDirectoryLoader
import os
import re
from dotenv import load_dotenv
from langchain_community.vectorstores import Pinecone as PinecineLangchain
from pinecone import Pinecone, PodSpec
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from typing import Any, Dict, List
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
load_dotenv()

OPENAI_API_KEY = os.getenv("SECRET_KEY")
_pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


# * parse JSON
def parse_json(text):
    object_pattern = r'\{.*?\}'
    pair_pattern = r'"(.*?)":\s*"(.*?)"'
    objects = re.findall(object_pattern, text, re.DOTALL)
    dict_list = []

    for obj in objects:
        pairs = re.findall(pair_pattern, obj)
        d = {key: value for key, value in pairs}
        dict_list.append(d)

    return dict_list


# * File embedding
def handle_file_embedding(file_path: str, pass_in_index_name: str):
    files = os.listdir(file_path)
    print("files", files)

    indexes = _pinecone.list_indexes()
    print("indexes", indexes.indexes)
    if not any(d['name'] == pass_in_index_name for d in indexes.indexes):
        _pinecone.create_index(
            name=pass_in_index_name,
            dimension=3072,
            metric="cosine",
            spec=PodSpec(
                environment="gcp-starter",
                pod_type="p1.x1",
            )
        )

    loader = PyPDFDirectoryLoader(file_path)
    doc = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, chunk_overlap=50, separators=["\n\n", "\n", " ", ""])
    documents = text_splitter.split_documents(doc)
    print(f"Number of documents: {len(documents)}")
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", api_key=OPENAI_API_KEY)
    PinecineLangchain.from_documents(
        documents, embeddings, index_name=pass_in_index_name)
    print("File embedded successfully")


# * Start conversation
def start_conversation(query: str, pass_in_index_name: str, chat_history: List[Dict[str, Any]] = []):

    print("chat_history", chat_history)

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large", api_key=OPENAI_API_KEY)
    search = PinecineLangchain.from_existing_index(
        embedding=embeddings, index_name=pass_in_index_name)

    chat = ChatOpenAI(verbose=True, temperature=0,
                      api_key=OPENAI_API_KEY, model="gpt-4-0125-preview")

    chain = ConversationalRetrievalChain.from_llm(
        llm=chat, retriever=search.as_retriever(), return_source_documents=True)

    return chain.invoke({"question": query, "chat_history": chat_history})


# * Generate MCQ from document
def generate_mcq_from_document(summarization: str, num_questions: int):
    response_schemas = [
        ResponseSchema(
            name="question", description="A multiple choice question generated from input text snippet."),
        ResponseSchema(
            name="option_1", description="First option for the multiple choice question. Use this format: 'a) option'"),
        ResponseSchema(
            name="option_2", description="Second option for the multiple choice question. Use this format: 'b) option'"),
        ResponseSchema(
            name="option_3", description="Third option for the multiple choice question. Use this format: 'c) option'"),
        ResponseSchema(
            name="option_4", description="Fourth option for the multiple choice question. Use this format: 'd) option'"),
        ResponseSchema(
            name="answer", description="Correct answer for the question. Use this format: 'd) option' or 'b) option', etc. Please give some explanation for the answer along with the source.")
    ]
    output_parser = StructuredOutputParser.from_response_schemas(
        response_schemas)

    format_instructions = output_parser.get_format_instructions()
    print(format_instructions)

    chat = ChatOpenAI(verbose=True, temperature=0, api_key=OPENAI_API_KEY,
                      model="gpt-4-0125-preview")

    prompt = ChatPromptTemplate(
        messages=[
            HumanMessagePromptTemplate.from_template("""When a text input is given by the llm summarization tool, please generate {num_questions} multiple choice questions 
        from it along with the correct answer. 
        \n{format_instructions}\n{user_prompt}""")
        ],
        input_variables=["user_prompt"],
        partial_variables={
            "format_instructions": format_instructions, "num_questions": num_questions}
    )

    user_query = prompt.format_prompt(user_prompt=summarization)
    return chat.invoke(user_query.to_messages())

    # return_json = parse_json(user_query_output.content)
    # print(return_json)

    # return return_json
