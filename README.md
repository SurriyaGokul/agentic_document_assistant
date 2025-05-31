# Document AI Assistant

**Intelligent Document Analysis and Processing with Streamlit, LangChain, and Ollama**

**Document AI Assistant** is a powerful and intuitive Streamlit application designed for intelligent document analysis. It seamlessly processes various file formats, including PDFs, JSON files, and emails.

---

## Key Features

* **Email Agent:** Automatically extracts structured metadata from `.eml` files, identifying sender, recipient, subject, message intent, and urgency.
* **PDF Agent:** Delivers concise summaries and extracts key information, insights, and data points from PDF documents.
* **JSON Agent:** Validates JSON data structures, parses content, and intelligently flags anomalies or inconsistencies.
* **In-Memory Storage:** Utilizes a centralized memory system for storing intermediate results, enabling efficient task chaining and seamless downstream operations.
* **Extensible Architecture:** Designed with a plug-and-play pattern, allowing for the easy addition of new document types or custom processing agents.
* **User-Friendly Interface:** Built with Streamlit for an interactive and easy-to-navigate user experience.

---

## Video Demonstration
[▶️ Watch the demo video](https://github.com/yourusername/yourrepo/blob/main/path/to/demo.mp4)


---

## Installation

Setting up the Document AI Assistant is straightforward. Follow these steps:

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/SurriyaGokul/GenAI.git
   cd GenAI
   ```

2. **Install Dependencies:**
   Ensure you have Python 3.8 or higher installed. Then, install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

   *(It’s recommended to use a virtual environment.)*

3. **Ollama Setup:**
   This project relies on Ollama for local LLM execution.

   * Install [Ollama](https://ollama.com/)
   * Pull the necessary models (e.g., `ollama pull llama3`). Refer to LangChain documentation for model compatibility.

---

## Usage

The Document AI Assistant can be run as a Streamlit application or used programmatically through its agents.

### Running the Streamlit Application

```bash
streamlit run main.py
```

### Programmatic Usage of Agents

Examples of using the individual agents:

#### Email Processing

```python
from agents.load_email import email_agent

try:
    result = email_agent("path/to/your/email.eml")
    print(result)
except FileNotFoundError:
    print("Error: Email file not found. Please check the path.")
except Exception as e:
    print(f"An error occurred during email processing: {e}")
```

#### PDF Processing

```python
from agents.load_pdf import pdf_agent

try:
    summary = pdf_agent("path/to/your/document.pdf")
    print(summary)
except FileNotFoundError:
    print("Error: PDF file not found. Please check the path.")
except Exception as e:
    print(f"An error occurred during PDF processing: {e}")
```

#### JSON Validation

```python
from agents.load_json import json_agent

try:
    results = json_agent("path/to/your/data.json")
    print(results)
except FileNotFoundError:
    print("Error: JSON file not found. Please check the path.")
except Exception as e:
    print(f"An error occurred during JSON processing: {e}")
```

---

## Project Structure

```
GenAI/
│
├── agents/                # Core processing agents for different document type
│   ├── load_email.py      # Agent for .eml file processing
│   ├── load_pdf.py        # Agent for .pdf file processing
│   └── load_json.py       # Agent for .json file validation and parsing
│
├── memory/                # In-memory storage system
│   ├── __init__.py
│   └── memory_store.py    # Shared memory implementation
│
├── test_files/            # Sample input files for testing and demonstration
│   ├── sample.eml
│   ├── sample.pdf
│   └── sample.json
│
├── .gitignore             # Specifies intentionally untracked files
├── requirements.txt       # Project dependencies
├── README.md              # This documentation file
└── main.py                 # Main Streamlit application script (if applicable)
```

---

## How It Works

The Document AI Assistant operates through a synergistic combination of specialized agents and core backend technologies:

* **Agents:**
  Each agent (`load_email.py`, `load_pdf.py`, `load_json.py`) is tailored for a specific document type and handles:

  * File Ingestion: Loading and parsing the input file.
  * Preprocessing: Preparing data for the language model.
  * Prompt Engineering: Constructing effective prompts for the LLM.
  * LLM Interaction: Communicating with the LLM via LangChain.
  * Result Storage: Storing processed information in the shared memory module.

* **LangChain + Ollama:**
  This powerful duo forms the core of the AI capabilities.

  * **LangChain:** Provides tools for model interaction, chaining, and prompt management.
  * **Ollama:** Runs open-source language models (like Llama 3, Mistral) locally, ensuring privacy and control.

* **Shared Memory (`memory_store.py`):**
  A lightweight key-value in-memory store that enables:

  * Caching: Avoiding redundant LLM calls.
  * Inter-Agent Communication: Sharing context between different parts of the system.

---

## Adding New Agents

The modular design allows easy extension for new document formats or tasks.

1. **Create Agent File:**
   Add a new Python file in the `agents/` directory (e.g., `load_docx.py`).

2. **Implement Agent Logic:**

   * Define loading and parsing functions.
   * Preprocess the document.
   * Design prompts tailored for your task.
   * Parse and return structured results.

3. **Use Shared Memory (Optional):**
   Integrate with `InMemorySharedMemory` for context sharing.

4. **Streamlit UI Integration (Optional):**
   Add UI elements for the new agent if needed.

---

## Requirements

* **Python:** 3.8 or higher
* **Core Libraries:**

  * [Streamlit](https://streamlit.io/): For the web UI.
  * [LangChain](https://python.langchain.com/): For LLM orchestration.
  * [Ollama](https://ollama.com/): For local LLM execution.

See `requirements.txt` for a complete list of dependencies.

---

### License

This project is licensed under the **MIT License**. See the [LICENSE](https://opensource.org/licenses/MIT) file for details.  

---

### Author

**Surriya Gokul**  
GitHub: [@SurriyaGokul](https://github.com/SurriyaGokul)  
---

> **Important Note:** Ensure that the necessary Ollama models (e.g., Llama 3, Mistral) are downloaded and running locally for the `ChatOllama` integration to function correctly. You can manage models using the Ollama CLI.
