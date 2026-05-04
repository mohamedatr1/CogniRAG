<div align="center">

<img src="https://img.shields.io/badge/CogniRAG-v1.0-6366f1?style=for-the-badge&logo=lightning&logoColor=white" />

# ⚡ CogniRAG

**Production-ready Retrieval-Augmented Generation system**  
*Ask questions about any document — PDF or URL — with full session isolation*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![LangChain](https://img.shields.io/badge/LangChain-0.3%2B-1c3c3c?style=flat-square)](https://langchain.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5%2B-ff6b35?style=flat-square)](https://trychroma.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-ff4b4b?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

</div>

---

## ✨ Features

| Feature | Details |
|---|---|
| 📄 **Multi-source ingestion** | PDF files + any public URL (Wikipedia, news, blogs, docs...) |
| 🔀 **MMR Retrieval** | Maximal Marginal Relevance for diverse, non-redundant results |
| ⚡ **Streaming** | Token-by-token streaming responses in the UI |
| 🔒 **Session isolation** | Full reset without file-lock errors (Windows-safe) |
| 📊 **Relevance scoring** | Every source chunk shows its similarity score |
| 🔌 **REST API** | FastAPI backend with streaming endpoint |
| 🧪 **Test suite** | pytest coverage for all core components |
| 🖥️ **Modern UI** | Dark, minimal Streamlit interface with live stats |

---

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/mohamedatr1/CogniRAG.git
cd CogniRAG
```

### 2. Install

```bash
pip install -r requirements.txt
```

### 3. Configure

Create a `.env` file in the project root:

```env
# ------------------------------------------------------------------------------
# GROQ API (Required for LLM)
# ------------------------------------------------------------------------------
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama3-70b-8192   # Options: llama3-70b-8192, mixtral-8x7b-32768, gemma2-9b-it

# ------------------------------------------------------------------------------
# Embeddings (OpenAI or HuggingFace) - Groq does not provide embeddings yet
# ------------------------------------------------------------------------------
OPENAI_API_KEY=your_openai_api_key_here   # Required if EMBEDDING_MODEL=openai
EMBEDDING_MODEL=openai                    # or "huggingface"
HUGGINGFACE_EMBEDDING_MODEL=all-MiniLM-L6-v2

# ------------------------------------------------------------------------------
# Vector Store
# ------------------------------------------------------------------------------
VECTOR_STORE_TYPE=chroma                  # chroma, pinecone, qdrant
PERSIST_DIRECTORY=./chroma_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=4

# ------------------------------------------------------------------------------
# Fallback LLM (optional, if Groq fails)
# ------------------------------------------------------------------------------
OLLAMA_BASE_URL=http://localhost:11434
```

> **Free Groq API key:** [console.groq.com](https://console.groq.com) — takes 30 seconds.

### 4. Run

**Streamlit UI:**
```bash
streamlit run ui/streamlit_app.py
```

---

## 🔧 Configuration

All settings live in `config/settings.py` and can be overridden via `.env`:

| Variable | Default | Description |
|---|---|---|
| `GROQ_API_KEY` | — | Groq API key (required for LLM) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `EMBEDDING_MODEL` | `huggingface` | `huggingface` or `openai` |
| `HUGGINGFACE_EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace model |
| `PERSIST_DIRECTORY` | `./chroma_db` | ChromaDB storage path |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `TOP_K` | `4` | Chunks retrieved per query |

---

## 🖥️ Streamlit UI

```
streamlit run ui/streamlit_app.py
```

**Sidebar controls:**
- Ingest URLs or PDFs
- Toggle MMR retrieval mode
- Toggle streaming mode
- Adjust Top-K
- View indexed sources
- New Chat / Reset All

**Right panel:**
- Live chunk count
- Avg response time
- Per-response timing + citations
- Ingest history

---


<div align="center">

Built by [@mohamedatr1](https://github.com/mohamedatr1)

</div>
