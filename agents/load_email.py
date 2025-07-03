from langchain_community.document_loaders import UnstructuredEmailLoader
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.prompts import PromptTemplate
import json
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memory.memory_store import LRUCacheTTL

# Defining the Cache Memory
cached_memory = LRUCacheTTL(max_size=1000, ttl_seconds=3600)

def email_agent(file_path: str):
    """
    Processes an email file to extract structured information using a language model.
    """
    # Load the email file
    loader = UnstructuredEmailLoader(file_path=file_path)
    documents = loader.load()
    email_text = "\n\n".join(doc.page_content for doc in documents)

    # Define the prompt
    prompt = PromptTemplate(
        input_variables=["context"],
        template="""
        You are a helpful assistant that extracts structured information from emails.

        Given this email content:
        ---
        {context}
        ---

        Extract the following as a JSON object with the following fields:
        - Sender (Name of the sender)
        - Intent (short phrase like "return request", "complaint", etc.)
        - Urgency (high, medium, or low)
        
        Ensure the output is a valid JSON object. Do not include any extra explanation or commentary.

        """
    )

    # Run the LLM
    llm = ChatOllama(model="llama3.1:8b", temperature=0.1)
    formatted_prompt = prompt.format(context=email_text)
    input_key = hash(formatted_prompt)
    cached_data = cached_memory.get(input_key)

    if cached_data:
        response_text = cached_data
        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            parsed = {"sender": None, "intent": None, "urgency": None}
    else:
        response = llm.invoke(formatted_prompt)
        response_text = response.content if hasattr(response, 'content') else str(response)

        try:
            parsed = json.loads(response_text)
        except json.JSONDecodeError:
            parsed = {"sender": None, "intent": None, "urgency": None}

        # Save to memory
        cached_memory.save(input_key, {
            "source": file_path,
            "type": "email",
            "values": email_text,
            "sender": parsed.get("sender"),
            "intent": parsed.get("intent"),
            "urgency": parsed.get("urgency")
        })

    print(f"LLM Response: {response_text}")
    return parsed 
