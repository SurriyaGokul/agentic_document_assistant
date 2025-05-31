# Document AI Assistant

**Document AI Assistant** is a Streamlit-powered application for intelligent document analysis and processing. It supports various formats—including PDFs, JSON files, and email messages—by leveraging state-of-the-art language models for structured information extraction, content validation, and summarization.

Built with the **LangChain** framework and integrated with **Ollama LLMs**, this modular system provides a robust foundation for automating document workflows with minimal setup.

---

##  Key Features

* **Email Agent**
  Automatically extracts structured metadata from `.eml` files, including sender identity, message intent, and urgency classification.

* **PDF Agent**
  Summarizes document content and identifies key information from PDF files.

* **JSON Agent**
  Validates and parses JSON data while flagging anomalies or inconsistencies.

* **In-Memory Storage**
  Stores intermediate results in a centralized memory system for chaining tasks and downstream operations.

* **Extensible Architecture**
  Easily add support for new document types or agents with a plug-and-play development pattern.

---

##  Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/SurriyaGokul/GenAI.git
   cd GenAI
   ```

2. **Install Required Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

##  Usage

### Email Processing

Extract sender details, intent, and urgency from an email:

```python
from agents.load_email import email_agent

result = email_agent("path/to/email.eml")
print(result)
```

### PDF Processing

Generate a summary and extract salient points from a PDF:

```python
from agents.load_pdf import pdf_agent

summary = pdf_agent("path/to/document.pdf")
print(summary)
```

### JSON Validation

Analyze and validate JSON data structures:

```python
from agents.load_json import json_agent

results = json_agent("path/to/data.json")
print(results)
```

---

##  Project Structure

```
GenAI/
│
├── agents/              # Document-specific agents
│   ├── load_email.py
│   ├── load_pdf.py
│   └── load_json.py
│
├── memory/              # In-memory storage system
│   └── memory_store.py
│
├── test_files/          # Sample input files for testing
├── requirements.txt     # Project dependencies
└── README.md            # Documentation
```

---

##  How It Works

* **Agents** handle file ingestion, preprocessing, and prompt generation. Each agent calls an LLM via LangChain and stores results in memory.
* **LangChain + Ollama** are used for flexible prompt handling and efficient LLM integration.
* **Shared Memory** provides a lightweight key-value store for caching and inter-agent communication.

---

## Adding New Agents

To support a new document format:

1. Create a new agent in the `agents/` directory.
2. Implement file loading, LLM prompt construction, and result parsing.
3. Optionally store results in `InMemorySharedMemory` for reuse.

---

## Requirements

* Python 3.8 or higher
* [LangChain](https://github.com/langchain-ai/langchain)
* [Ollama](https://ollama.com/) (for running local LLMs)
* Additional dependencies listed in `requirements.txt`

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

---

## Author

**[Surriya Gokul](https://github.com/SurriyaGokul)**

---

## Contributions

Contributions, issues, and feature requests are welcome!
Feel free to open an issue or submit a pull request to improve this project.

---

> **Note**: Ensure the necessary Ollama models are installed and running locally to enable full functionality with `ChatOllama`.

---

