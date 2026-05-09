# 🛡️ CTI Analyst Platform

An AI-powered Cyber Threat Intelligence platform built using FastAPI, Next.js, LangChain, and Ollama for automated threat analysis, RAG querying, vulnerability intelligence, and analyst reporting.

---

## 🚀 Features

- 🔐 JWT Authentication & Secure Analyst Workspaces
- 🧠 Hybrid RAG Pipeline (FAISS + BM25)
- 📄 AI-Powered Threat Intelligence Querying
- ⚠️ Live CVE & Vulnerability Intelligence
- 📊 Threat Classification & Risk Scoring
- 📝 Automated PDF Intelligence Report Generation
- 🗂️ Persistent Analyst History & Audit Logging
- ⚡ Modern Next.js Dashboard Interface
- ☁️ GitHub Version Control & CI/CD Ready
- 🌐 Free Cloud Deployment Support (Render + Vercel)

---

# 🏗️ Tech Stack

## Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- shadcn/ui
- Axios

## Backend
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL / SQLite
- JWT Authentication

## AI / RAG
- LangChain
- FAISS
- BM25
- Ollama
- qwen2.5-coder:7b

---

# 🧠 Architecture

```text
Next.js Frontend
       │
       ▼
FastAPI Backend
       │
 ┌─────┼─────┐
 ▼           ▼
Database    RAG Engine
                │
        ┌───────┴───────┐
        ▼               ▼
      FAISS           BM25
```

---

# 📁 Project Structure

```text
CTI/
│
├── frontend/                     # Next.js Frontend
│
├── backend/                      # FastAPI Backend
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── rag/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── alembic/
│   ├── requirements.txt
│   ├── .env
│   └── alembic.ini
│
├── database/
│   └── sqlite/
│
├── assets/
├── docs/
└── README.md
```

---

# ⚙️ Local Installation

## 1. Clone Repository

```bash
git clone https://github.com/sayeedur007-design/Cyber-Threat-Intel
cd Cyber-Threat-Intel
```

---

## 2. Backend Setup

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux / Mac
source venv/bin/activate

cd backend

pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Create a `.env` file inside the `backend/` directory.

Example:

```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///cti_app.db
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 4. Run Database Migrations

```bash
alembic upgrade head
```

---

## 5. Start Ollama

```bash
ollama run qwen2.5-coder:7b
```

---

## 6. Start Backend

```bash
uvicorn app.main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

Swagger Docs:

```text
http://127.0.0.1:8000/docs
```

---

## 7. Start Frontend

Open a new terminal:

```bash
cd frontend

npm install

npm run dev
```

Frontend runs on:

```text
http://localhost:3000
```

---

# 🌐 Deployment

## Frontend Deployment (Free)

Deploy the frontend using:

- Vercel

Frontend Root Directory:

```text
frontend
```

Environment Variable:

```env
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

---

## Backend Deployment (Free)

Deploy the backend using:

- Render

Backend Root Directory:

```text
backend
```

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Production URLs

Frontend:

```text
https://your-frontend.vercel.app
```

Backend:

```text
https://your-backend.onrender.com
```

---

# 🤖 Ollama Deployment Note

Ollama-based local LLM inference may not work properly on free cloud hosting platforms due to memory and runtime limitations.

For deployment demos:
- AI responses can be mocked
- External LLM APIs can be integrated later
- Local Ollama works fully during local development

---

# 📌 Example Capabilities

## Threat Intelligence Query

```text
What attack techniques are associated with LockBit ransomware?
```

---

## CVE Analysis

```text
CVE-2021-44228
```

---

## Generated Outputs

- Threat actor identification
- TTP analysis
- Risk scoring
- Vulnerability intelligence
- PDF intelligence reports

---

# 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Protected API routes
- Persistent audit logging
- ORM-based database security

---

# ☁️ GitHub Setup

## Initialize Git Repository

```bash
git init
git add .
git commit -m "Initial commit"
```

---

## Connect GitHub Repository

```bash
git remote add origin https://github.com/sayeedur007-design/Cyber-Threat-Intel
git branch -M main
git push -u origin main
```

---

# 📈 Future Improvements

- Docker Compose orchestration
- Redis caching
- SIEM integrations
- Elasticsearch support
- Kubernetes deployment
- Multi-agent workflows
- Streaming AI responses
- Cloud-hosted LLM integration

---

# ⚖️ License

This project is developed for educational, research, and cybersecurity demonstration purposes.