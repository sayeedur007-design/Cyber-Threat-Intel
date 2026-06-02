# CTI Analyst Platform — Quick Launch Guide

This file provides direct, simple instructions to launch the full Cyber Threat Intelligence (CTI) application in local development.

---

## 🚀 Application Ports & Services

Once launched, the services are accessible via the following links:

| Component | Service | Direct Link |
| :--- | :--- | :--- |
| **Frontend UI** | Next.js TypeScript Web App | [http://localhost:3000](http://localhost:3000) |
| **Backend API** | FastAPI Service Gateway | [http://localhost:8000](http://localhost:8000) |
| **API docs** | Interactive Swagger OpenAPI Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

## ⚡ Execution Commands

To run both services concurrently from a PowerShell or CMD terminal, follow these steps:

### 1. Start the FastAPI Backend
Open a terminal in the project root and execute the following:
```powershell
cd backend
# Activate virtual environment
.\venv\Scripts\activate

# Start the uvicorn development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Start the Next.js Frontend
Open a **new** terminal in the project root and execute:
```powershell
cd frontend
# Launch Next.js dev server
npm run dev
```

---

## 🧠 Prerequisites
1. **Ollama Integration**: Make sure your local Ollama instance is running and has the target model pulled:
   ```bash
   ollama run qwen2.5-coder:7b
   ```
2. **Database State**: The FastAPI backend automatically checks database connections on startup and programmatically runs all migrations on our SQLite database (`cti_database.db`). No manual DB configurations are needed.
