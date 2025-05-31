import streamlit as st
from langchain_community.chat_models import ChatOllama
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate
from langchain.tools.render import render_text_description
from langchain_community.document_loaders import PyPDFLoader
from agents.load_json import json_agent
from agents.load_pdf import pdf_agent
from agents.load_email import email_agent
from memory.memory_store import InMemorySharedMemory
import tempfile
import os

# Shared memory object
memory = InMemorySharedMemory()

# Document reader
# def read_file(file_path: str) -> str:
#     if file_path.endswith(".pdf"):
#         loader = PyPDFLoader(file_path)
#         pages = loader.load()
#         return "\n".join(page.page_content for page in pages)
#     else:
#         with open(file_path, 'r', encoding='utf-8') as f:
#             return f.read()

# Prompt template for ReAct agent
REACT_PROMPT_TEMPLATE = """
You are an expert document processing assistant. Your goal is to analyze the provided document file path and route it to the most appropriate tool for processing. 

You have access to the following tools:
{tools}

Use the following format for your thought process and actions:

Question: The document content or a query related to it.
Thought: Carefully analyze the document content. Determine its type (e.g., PDF, JSON, Email) and its primary purpose or intent. Based on this, decide which tool is best suited to process it.
Action: The action to take, must be one of [{tool_names}].
Action Input: The full file path of the document that needs to be processed by the selected tool. Pass the file path to the tool.
Observation: The result returned by the tool after processing.
Thought: I have now processed the document with the selected tool and have the result.
Final Answer: The result obtained from the tool.

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""

# Agent executor logic
def run_agent(file_path: str, thread_id: str = "default", initial_content: str = None) -> dict:
    if initial_content is None:
        content = file_path
    else:
        content = initial_content
    tools = [
        Tool(name="pdf_agent", func=lambda x: pdf_agent(x, thread_id), description="Use this tool to process content from PDF documents. Input should be the full text content of the PDF."),
        Tool(name="json_agent", func=lambda x: json_agent(x, thread_id), description="Use this tool to process content from JSON documents or data. Input should be the JSON string."),
        Tool(name="email_agent", func=lambda x: email_agent(x, thread_id), description="Use this tool to process content from Email documents. Input should be the full text content of the email.")
    ]

    prompt = PromptTemplate(
        template=REACT_PROMPT_TEMPLATE,
        input_variables=['input', 'agent_scratchpad', 'tools', 'tool_names']
    ).partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools])
    )

    llm = ChatOllama(model="gemma3:12b", temperature=0)

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

    try:
        result = executor.invoke({"input": content})
    except Exception as e:
        return {"error": f"Agent failed: {str(e)}"}

    memory.save(thread_id, {"source": file_path, "result": result})
    return result

# --- Streamlit UI ---
st.set_page_config(page_title="Document AI Assistant", layout="centered")

st.title("Document AI Assistant")
st.write("Upload a document (PDF, JSON, or plain text) and let the AI analyze and process it using appropriate tools.")

uploaded_file = st.file_uploader("Choose a document", type=["pdf", "json", "txt", "eml"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    thread_id = st.text_input("Thread ID", value="default")

    if st.button("Analyze Document"):
        with st.spinner("Processing..."):
            result = run_agent(file_path, thread_id)

        if "error" in result:
            st.error(result["error"])
        else:
            st.success("Document processed successfully!")
            st.subheader("Final Answer:")
            st.json(result.get("output", result))

            st.subheader("Memory Log")
            st.json(memory.get(thread_id))
