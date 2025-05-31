from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import ChatOllama  
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
import os
import sys

# Add the parent directory of 'memory' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.memory_store import InMemorySharedMemory


def extract_json(text):
    """Attempt to extract valid JSON object from a string response."""
    try:
        return json.loads(text)
    except:
        import re
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return {"summary": "No summary available", "key_information": []}


def pdf_agent(file_path: str, thread_id: str = "default") -> list:
    """
    Processes a PDF file, extracts chunks, summarizes each using LLM, 
    and stores content in shared memory.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    prompt = """
            You are a helpful assistant that extracts structured information from PDF documents.

            Given this PDF content:
            ---
            {context}
            ---

            Generate a summary of the document content and extract key information.
            Return the summary as a JSON object with the following fields:
            - summary (string): A brief summary of the document.
            - key_information (list): A list of key points or information extracted from the document.

            Ensure the output is a valid JSON object. Do not include any extra explanation or commentary.
        """

    print("Initializing LLM with model: llama3.1:8b")
    llm = ChatOllama(model="llama3.1:8b", temperature=0)
    prompt = PromptTemplate(
        input_variables=["context"],
        template=prompt)

    summaries = []
    for chunk in chunks:
        context = chunk.page_content
        print(f"Processing chunk of size {len(context)} characters")
        response = llm.invoke(prompt.format(context=context))
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)

        result = extract_json(response_text)
        summaries.append(result)

    shared_memory = InMemorySharedMemory()

    for doc in documents:
        entry = {
            "source": file_path,
            "type": "pdf",
            "values": doc.page_content
        }
        shared_memory.save(thread_id, entry)

    merged_summary = {
        "summary": " ".join(item["summary"] for item in summaries if "summary" in item),
        "key_information": [point for item in summaries for point in item.get("key_information", [])]
    }

    return merged_summary


