# Your project specification and notes

# 🚀 YieldExam: Local AI-Powered Past Paper Analytics & Revision Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B.svg)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791.svg)](https://github.com/pgvector/pgvector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**YieldExam** is a 100% local-first, privacy-focused past paper analytics application. It automatically parses exam PDF documents, extracts questions and mark allocations using local LLMs with strict JSON validation, maps them to a dynamic curriculum taxonomy, and calculates **"high-yield" analytics** to optimize student revision efficiency.

---

## ✨ Key Features

- **🔒 100% Local & Private Execution**: Runs entirely on your machine using **Ollama** (R0 API cost, zero data leaves your computer).
- **🎯 Structured AI Extraction**: Combines **Instructor** and **Pydantic** to enforce deterministic JSON outputs from local models, preventing AI hallucinations.
- **📊 High-Yield Mark Analytics**: Automatically calculates and ranks curriculum topics by cumulative mark weightings and question frequencies.
- **⚙️ Dynamic Scope Management**: Decoupled database architecture allowing flexible subject and syllabus swapping.
- **⚡ Modern Tech Stack**: Built with a **FastAPI** backend, **PostgreSQL (`pgvector`)** database, and an interactive **Streamlit** dashboard.

---

## 🏗️ Architecture & Tech Stack

```text
[ Past Paper PDF ] 
       │
       ▼
[ pdfplumber (Text Extraction) ] 
       │
       ▼
[ Ollama + Instructor (Local LLM structured JSON parsing) ]
       │
       ▼
[ PostgreSQL + SQLModel (Relational storage & vector embeddings) ]
       │
       ▼
[ FastAPI Backend REST Endpoints ]
       │
       ▼
[ Streamlit Interactive Dashboard ]