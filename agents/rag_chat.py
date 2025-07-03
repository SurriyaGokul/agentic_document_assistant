from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
import hashlib
import os

def get_file_hash(file_path):
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def build_vectorstore(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    return vectorstore

def get_rag_chain(file_path):
    file_hash = get_file_hash(file_path)
    vectorstore = build_vectorstore(file_path)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    llm = ChatOllama(model="llama3.1:8b", temperature=0)

    chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    return chain
