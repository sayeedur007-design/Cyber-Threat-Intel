# 🛡️ CTI Analyst Platform  

> 🚀 AI-Powered Cyber Threat Intelligence & Vulnerability Analysis Platform  
> Built for security analysts, researchers, and cybersecurity demonstrations.

---

## 🌐 Live Deployment

### 🔗 Production Links

- 🌍 **Frontend (Vercel):**  
  https://cyber-threat-intel-qu0pvd81j-sayeedur007-designs-projects.vercel.app/login

- ⚡ **Backend API (Railway):**  
  https://railway.com/project/5032e912-e1c8-4f17-874f-c4b45a8e2371

- 🗄️ **PostgreSQL Database (Railway):**  
  https://railway.com/project/5032e912-e1c8-4f17-874f-c4b45a8e2371/service/b999a216-65e1-44ca-b8ba-f809facb9e1f/database?environmentId=b0d2d06c-17c7-4b51-a54a-bee757e3a900

- 💻 **GitHub Repository:**  
  https://github.com/sayeedur007-design/Cyber-Threat-Intel

---

# 🧠 About The Project

CTI Analyst Platform is an AI-powered Cyber Threat Intelligence system designed to automate threat analysis, vulnerability intelligence, and security investigation workflows using modern AI + RAG architecture.

The platform combines:
- 🧠 Retrieval-Augmented Generation (RAG)
- 🔎 Threat Intelligence Querying
- ⚠️ CVE & Vulnerability Analysis
- 📄 Automated Intelligence Reports
- 📊 Threat Risk Scoring
- 🔐 Secure Analyst Authentication

---

# ✨ Core Features

## 🔐 Security & Authentication
- JWT Authentication
- Secure Analyst Workspaces
- Password Hashing with bcrypt
- Protected API Routes
- Persistent Audit Logging

---

## 🧠 AI & Threat Intelligence
- Hybrid RAG Pipeline (FAISS + BM25)
- AI-Powered Threat Querying
- Threat Actor Intelligence
- TTP Analysis
- Threat Classification
- Risk Scoring Engine

---

## ⚠️ Vulnerability Intelligence
- Live CVE Analysis
- Vulnerability Enrichment
- Threat Correlation
- Security Context Generation

---

## 📄 Reporting & Analytics
- Automated PDF Intelligence Reports
- Analyst Query History
- Threat Investigation Workflow
- Modern Dashboard UI

---

# 🏗️ System Architecture

```text
                 ┌──────────────────────┐
                 │   Next.js Frontend   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   FastAPI Backend    │
                 └──────────┬───────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                                   ▼
┌──────────────────┐              ┌────────────────────┐
│ PostgreSQL DB    │              │     RAG Engine     │
└──────────────────┘              └─────────┬──────────┘
                                            │
                          ┌─────────────────┴─────────────────┐
                          ▼                                   ▼
                    ┌──────────────┐                  ┌──────────────┐
                    │    FAISS     │                  │     BM25     │
                    └──────────────┘                  └──────────────┘
```

---

# 🛠️ Tech Stack

## 🎨 Frontend
- ⚡ Next.js 14
- 🟦 TypeScript
- 🎨 Tailwind CSS
- 🧩 shadcn/ui
- 🔗 Axios

---

## ⚙️ Backend
- 🚀 FastAPI
- 🗄️ SQLAlchemy
- 🔄 Alembic
- 🐘 PostgreSQL
- 🔐 JWT Authentication

---

## 🤖 AI / RAG Stack
- 🧠 LangChain
- 📚 FAISS Vector Store
- 🔍 BM25 Retrieval
- 🦙 Ollama
- 🤖 qwen2.5-coder:7b

---

# 📂 Project Structure

```text
CTI/
│
├── frontend/                  # Next.js Frontend
│
├── backend/                   # FastAPI Backend
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
├── assets/
├── docs/
└── README.md
```

---

# ⚡ Local Installation

## 1️⃣ Clone Repository

```bash
git clone https://github.com/sayeedur007-design/Cyber-Threat-Intel
cd Cyber-Threat-Intel
```

---

## 2️⃣ Backend Setup

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

## 3️⃣ Configure Environment Variables

Create a `.env` file inside `backend/`

```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

DATABASE_URL=postgresql://username:password@host:port/dbname

OLLAMA_BASE_URL=http://localhost:11434
```

---

## 4️⃣ Run Database Migrations

```bash
alembic upgrade head
```

---

## 5️⃣ Start Ollama

```bash
ollama run qwen2.5-coder:7b
```

---

## 6️⃣ Start Backend

```bash
uvicorn app.main:app --reload
```

### Backend URL

```text
http://127.0.0.1:8000
```

### Swagger Documentation

```text
http://127.0.0.1:8000/docs
```

---

## 7️⃣ Start Frontend

```bash
cd frontend

npm install

npm run dev
```

### Frontend URL

```text
http://localhost:3000
```

---

# 🌍 Deployment Stack

| Service | Platform |
|---|---|
| 🎨 Frontend | Vercel |
| ⚙️ Backend | Railway |
| 🗄️ Database | PostgreSQL (Railway) |
| 💻 Version Control | GitHub |

---

# 🔍 Example Threat Queries

## 🦠 Malware Intelligence

```text
What attack techniques are associated with LockBit ransomware?
```

---

## ⚠️ CVE Investigation

```text
CVE-2021-44228
```

---

## 🎯 Generated Intelligence Outputs

- Threat Actor Identification
- Attack Technique Analysis
- Risk Scoring
- Vulnerability Intelligence
- Security Recommendations
- PDF Intelligence Reports

---

# 📸 Platform Highlights

- 🧠 AI Threat Investigation
- ⚠️ Vulnerability Intelligence
- 📊 Risk Assessment
- 📄 Analyst Reporting
- 🔐 Secure Authentication
- ☁️ Cloud Deployment Ready

---

# 🚀 Future Improvements

- 🐳 Docker Deployment
- ⚡ Redis Caching
- 📡 SIEM Integration
- 🔎 Elasticsearch Support
- ☸️ Kubernetes Deployment
- 🤖 Multi-Agent AI Workflows
- 🌊 Streaming AI Responses
- ☁️ Hosted LLM APIs

---

# 📜 License

This project is developed for:
- 🎓 Educational Purposes
- 🔬 Cybersecurity Research
- 🛡️ Threat Intelligence Demonstrations

---

# ⭐ Support The Project

If you found this project useful:

🌟 Star the repository  
🍴 Fork the project  
🛠️ Contribute improvements  

---

# 👨‍💻 Developer

Developed by **Sayeedur Rahman**  
Cybersecurity • AI • Threat Intelligence