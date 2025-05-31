from langchain_community.document_loaders import JSONLoader
from langchain_core.tools import tool
from memory.memory_store import InMemorySharedMemory
import json

def validate_document(doc: dict) -> list:
    errors = []
    for key, value in doc.items():
        if value in (None, "", [], {}, float("nan")):
            errors.append(f"Field '{key}' is empty or invalid")
    return errors


shared_memory = InMemorySharedMemory()


def json_agent(file_path: str, thread_id: str = "default") -> list:
    """
    Processes a JSON file, validates its content, and saves the results to shared memory.

    Args:
        file_path (str): The path to the JSON file to be loaded and processed.
        thread_id (str, optional): The identifier for the thread in shared memory. Defaults to "default".

    Returns:
        list: A list containing a dictionary with the processed JSON content, its type, 
              any validation anomalies, and the source. If a JSON decoding error occurs, 
              returns a list with an error dictionary containing the error message.
    """
    print("Processing JSON file:", file_path)
    loader = JSONLoader(file_path=file_path, jq_schema=".", text_content=False)  # Set text_content=False
    documents = loader.load()
    try:
        for doc in documents:
            reformatted = json.loads(doc.page_content)  # Parse page_content into a dictionary
            anomalies = validate_document(reformatted)
            result = {
                "source": file_path,
                "type": "json",
                "values": reformatted,
                "anomalies": anomalies
            }
            shared_memory.save(thread_id, result)
            return [result]
    except json.JSONDecodeError as e:
        return [{"source": file_path, "type": "json", "error": str(e)}]

