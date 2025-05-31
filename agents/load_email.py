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
from memory.memory_store import InMemorySharedMemory

def email_agent(file_path: str, thread_id: str = "default"):
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
    response = llm.invoke(formatted_prompt)

    # Extract content from the AIMessage object
    response_text = response.content if hasattr(response, 'content') else str(response)

    print(f"LLM Response: {response_text}")

    # Parse the LLM response
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        parsed = {"sender": None, "intent": None, "urgency": None}

    # Save to memory
    shared_memory = InMemorySharedMemory()
    shared_memory.save(thread_id, {
        "source": file_path,
        "type": "email",
        "values": email_text,
        "sender": parsed.get("sender"),
        "intent": parsed.get("intent"),
        "urgency": parsed.get("urgency")
    })

    return parsed 
