from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import ChatOllama  
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
import os
import sys
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.memory_store import LRUCacheTTL  

cache = LRUCacheTTL(max_size=1000, ttl_seconds=3600)

def extract_json(text):
    """Attempt to extract valid JSON object from a string response."""
    try:
        return json.loads(text)
    except:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return {"summary": "No summary available", "key_information": []}


def pdf_agent(file_path: str) -> dict:
    """
    Processes a PDF file, extracts chunks, summarizes each using LLM, 
    and caches results with LRU + TTL logic.
    """
    loader = PyPDFLoader(file_path)
    documents = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    prompt_template = PromptTemplate(
        input_variables=["context"],
        template="""
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
    )

    print("Initializing LLM with model: llama3.1:8b")

    llm = ChatOllama(model="llama3.1:8b", temperature=0)

    summaries = []
    for chunk in chunks:
        context = chunk.page_content
        input_key = hash(context)

        print(f"Processing chunk of size {len(context)} characters")

        cached_result = cache.get(input_key)
        if cached_result:
            summaries.append(cached_result)
            continue

        response = llm.invoke(prompt_template.format(context=context))
        response_text = response.content if hasattr(response, 'content') else str(response)
        parsed_result = extract_json(response_text)

        cache.put(input_key, parsed_result)
        summaries.append(parsed_result)

    merged_summary = {
        "summary": " ".join(item["summary"] for item in summaries if "summary" in item),
        "key_information": [point for item in summaries for point in item.get("key_information", [])]
    }

    return merged_summary
