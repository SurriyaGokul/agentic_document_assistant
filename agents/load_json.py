from langchain_community.document_loaders import JSONLoader
from langchain_core.tools import tool
from memory.memory_store import LRUCacheTTL 
import json

def validate_document(doc: dict) -> list:
    errors = []
    for key, value in doc.items():
        if value in (None, "", [], {}, float("nan")):
            errors.append(f"Field '{key}' is empty or invalid")
    return errors

cache = LRUCacheTTL(max_size=1000, ttl_seconds=3600)

def json_agent(file_path: str) -> list:
    """
    Processes a JSON file, validates its content, and caches the results using LRU + TTL.

    Returns:
        list: A list with a dict containing structured result or error message.
    """

    print("Processing JSON file:", file_path)

    loader = JSONLoader(file_path=file_path, jq_schema=".", text_content=False)
    documents = loader.load()

    try:
        for doc in documents:
            reformatted = json.loads(doc.page_content)
            input_key = hash(json.dumps(reformatted, sort_keys=True))  

            cached_result = cache.get(input_key)
            if cached_result:
                return [cached_result]
            
            anomalies = validate_document(reformatted)
            result = {
                "source": file_path,
                "type": "json",
                "values": reformatted,
                "anomalies": anomalies
            }

            cache.put(input_key, result)
            return [result]

    except json.JSONDecodeError as e:
        return [{"source": file_path, "type": "json", "error": str(e)}]
