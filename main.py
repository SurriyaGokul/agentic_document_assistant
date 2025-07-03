import streamlit as st
import tempfile, os
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import Tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools.render import render_text_description
from agents.load_pdf import pdf_agent
from agents.load_json import json_agent
from agents.load_email import email_agent
from agents.rag_chat import get_rag_chain  
from memory.memory_store import LRUCacheTTL

# Shared memory for ReAct results
cached_memory = LRUCacheTTL(max_size=1000, ttl_seconds=3600)

# ReAct Prompt
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

# Run ReAct agent
def run_agent(file_path: str) -> dict:
    tools = [
        Tool(name="pdf_agent", func=lambda x: pdf_agent(x), description="Processes PDF documents."),
        Tool(name="json_agent", func=lambda x: json_agent(x), description="Processes JSON files."),
        Tool(name="email_agent", func=lambda x: email_agent(x), description="Processes Email files."),
    ]

    prompt = PromptTemplate(
        template=REACT_PROMPT_TEMPLATE,
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"]
    ).partial(
        tools=render_text_description(tools),
        tool_names=", ".join([t.name for t in tools])
    )

    llm = ChatOllama(model="gemma3:12b", temperature=0)
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    cached_data = cached_memory.get(hash(file_path))
    if cached_data:
        return cached_data["result"]
    
    result = executor.invoke({"input": file_path})
    cached_memory.put(hash(file_path), {"result": result})
    return result

# --- Streamlit UI ---
st.set_page_config(page_title="Document AI Assistant", layout="centered")
st.title("Document AI Assistant")

st.write("Upload a document (PDF, JSON, EML) and choose a mode:")

uploaded_file = st.file_uploader("Choose a document", type=["pdf", "json", "txt", "eml"])
mode = st.radio("Choose mode", ["Analyze (ReAct)", "Chat with Document (RAG)"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        file_path = tmp_file.name

    if mode == "Analyze (ReAct)":
        if st.button("Run ReAct Agent"):
            with st.spinner("Analyzing..."):
                result = run_agent(file_path)

            if "error" in result:
                st.error(result["error"])
            else:
                st.success("Document analyzed!")
                st.subheader("Final Answer:")
                st.json(result.get("output", result))

    elif mode == "Chat with Document (RAG)":
        rag_chain = get_rag_chain(file_path)

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_query = st.chat_input("Ask a question about the document:")
        if user_query:
            st.session_state.chat_history.append({"role": "user", "text": user_query})
            with st.spinner("Thinking..."):
                result = rag_chain({"question": user_query})
                answer = result["answer"]
                st.session_state.chat_history.append({"role": "assistant", "text": answer})

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.chat_message("user").markdown(msg["text"])
            else:
                st.chat_message("assistant").markdown(msg["text"])
