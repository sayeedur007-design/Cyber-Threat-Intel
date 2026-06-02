import os
import time
import json
import logging
import requests
import re
from typing import List, Optional
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI and Core Imports
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from sqlalchemy.orm import Session

# Local Imports
from app.core import database
from app.models import User, QueryHistory, ThreatLog
from app.api import auth
from app.services import report_generator
from app.rag.rag_engine import CTI_RAG_Engine
from app.services.threat_classifier import ThreatClassifier
from app.services.risk_scorer import RiskScorer


# Setup Logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("CTI-API")

app = FastAPI(title="CTI Analyst Backend API")

# Singletons (Initialized on startup)
_engine = None
_classifier = ThreatClassifier()
_risk_scorer = RiskScorer()

# --- DATABASE INITIALIZATION EVENT ---
@app.on_event("startup")
def startup_event():
    """
    Verify database connectivity on startup and eagerly initialize
    singletons like the CTI_RAG_Engine to prevent thread race conditions.
    """
    log.info("Checking database connection...")
    try:
        # Verify connectivity safely
        database.check_db_connection()
        log.info("Database connection verified successfully.")

        # Eagerly initialize RAG Engine singleton to prevent lazy-load race conditions under load
        global _engine
        log.info("Eagerly initializing RAG Engine singleton...")
        _engine = CTI_RAG_Engine()
        log.info("RAG Engine singleton loaded successfully.")

        # If using local SQLite, run migrations programmatically for developer convenience
        if database.SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
            log.info("SQLite database detected. Running migrations automatically...")
            from alembic.config import Config
            from alembic import command
            
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ini_path = os.path.join(backend_dir, "alembic.ini")
            
            cfg = Config(ini_path)
            cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))
            command.upgrade(cfg, "head")
            log.info("Local SQLite database migrations completed successfully.")
            
    except Exception as e:
        log.error(f"Database initialization/migration failed: {e}")
        # CRITICAL: Raise the exception on startup failure so production environments crash
        # instead of running in a degraded/broken state!
        raise e

# FastAPI throws a runtime error if allow_credentials=True is combined with a wildcard '*' origin.
# Allowed origins are loaded dynamically from environment variables to isolate production domains from local configurations.
cors_origins_raw = os.getenv("CORS_ORIGINS", "")
if cors_origins_raw:
    origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]
else:
    origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://cti-analyst-platform.vercel.app",
    ]

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_engine() -> CTI_RAG_Engine:
    global _engine
    if _engine is None:
        _engine = CTI_RAG_Engine()
    return _engine

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Question query text")

class ClassifyRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text snippet to classify")

class VulnerabilityItem(BaseModel):
    id: str
    severity: str
    description: str

class ReportRequest(BaseModel):
    query: str = ""
    query_response: str = ""
    classification: str = ""
    classification_confidence: float = 0.0
    vulnerabilities: List[VulnerabilityItem] = []
    risk_score: float = 0.0
    risk_label: str = "Unknown"

def safe_json_parse(text: str, fallback=None):
    """Robustly extract and parse JSON from LLM output."""
    try:
        # Strategy 1: Find block matching [...] or {...}
        match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        
        # Strategy 2: Strip markdown artifacts
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except Exception as e:
        log.warning(f"JSON Parse failed: {e} | Content: {text[:100]}...")
        return fallback

# Helper to mimic Streamlit's UploadedFile
class FileProxy:
    def __init__(self, name, content):
        self.name = name
        self.content = content
    def getbuffer(self):
        return self.content

@app.get("/")
def health_check():
    return {"status": "online", "message": "CTI Analyst Backend is active."}

# --- AUTH ENDPOINTS ---

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique alphanumeric username")
    email: str = Field(..., max_length=100, pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Valid email address")
    password: str = Field(..., min_length=6, max_length=72, description="Plaintext password")

@app.post("/auth/register")
def register_user(user: UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User registered successfully"}

@app.post("/auth/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # Authenticate via username
    user = db.query(User).filter(User.username == form_data.username).first()
    # Alternatively authenticate via email if user entered email in username field
    if not user:
        user = db.query(User).filter(User.email == form_data.username).first()
        
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = auth.timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me")
def read_users_me(current_user: User = Depends(auth.get_current_user)):
    return {"username": current_user.username, "email": current_user.email}

# --- PROTECTED CTI ENDPOINTS ---

@app.post("/index")
async def index_documents(files: List[UploadFile] = File(...), current_user: User = Depends(auth.get_current_user)):
    engine = get_engine()
    proxies = []
    for f in files:
        content = await f.read()
        proxies.append(FileProxy(f.filename, content))
    
    # Run heavy vector-embedding/chunking tasks in threadpool to avoid blocking main event loop
    success, message = await run_in_threadpool(engine.process_files, proxies)
    if not success:
        raise HTTPException(status_code=500, detail=message)
    
    return {"success": True, "message": message, "chunks": engine.chunk_count}

@app.post("/query")
def query_intelligence(req: QueryRequest, current_user: User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    engine = get_engine()
    if engine.ensemble_retriever is None:
        return {"answer": "⚠️ No documents indexed yet. Please upload files first.", "context": [], "iocs": {}, "metrics": {}}
    
    result = engine.query(req.question)
    
    # Calculate Risk Score
    risk_text = result["answer"] + " " + " ".join([d.page_content for d in result["context"]])
    r_score = _risk_scorer.calculate(risk_text)
    
    result["risk"] = {
        "score": r_score,
        "label": _risk_scorer.get_label(r_score),
        "color": _risk_scorer.get_color(r_score)
    }
    
    # Log query history
    history_entry = QueryHistory(user_id=current_user.id, query=req.question, response=result["answer"])
    db.add(history_entry)
    db.commit()
    
    return result

@app.post("/rag-query")
def rag_query_endpoint(req: QueryRequest, current_user: User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    # This is an added endpoint to support the specific RAG frontend implementation
    engine = get_engine()
    if engine.ensemble_retriever is None:
        return {"answer": "⚠️ No documents indexed yet. Please upload files first.", "context": [], "iocs": {}, "metrics": {}}
    
    result = engine.query(req.question)
    result["confidenceScore"] = 0.85 # Simulated confidence score
    result["sources"] = [d.metadata.get('source', 'Unknown Source') for d in result["context"]]
    
    # Log query history
    history_entry = QueryHistory(user_id=current_user.id, query=req.question, response=result["answer"])
    db.add(history_entry)
    db.commit()
    
    return result

@app.get("/cve")
def search_cve(query: str = None, current_user: User = Depends(auth.get_current_user)):
    clean_query = query.strip() if query else None
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={clean_query}&resultsPerPage=5" if clean_query else \
          "https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=5"
        
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        cve_list = []
        for vuln in data.get("vulnerabilities", []):
            item = vuln.get("cve", {})
            cve_id = item.get("id", "Unknown ID")
            
            descriptions = item.get("descriptions", [])
            desc_text = next((d.get("value") for d in descriptions if d.get("lang") == "en"), "No description available.")
            
            metrics = item.get("metrics", {})
            cvss_score = 0.0
            cvss_severity = "N/A"
            
            for m_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
                m_list = metrics.get(m_key, [])
                if m_list:
                    cvss_data = m_list[0].get("cvssData", {})
                    cvss_score = cvss_data.get("baseScore", 0.0)
                    cvss_severity = cvss_data.get("baseSeverity") or m_list[0].get("baseSeverity", "N/A")
                    break

            r_score = _risk_scorer.calculate(desc_text, base_cvss=cvss_score)
            cve_list.append({
                "id": cve_id, "desc": desc_text, "score": cvss_score, "severity": str(cvss_severity).upper(),
                "risk_score": r_score, "risk_label": _risk_scorer.get_label(r_score), "risk_color": _risk_scorer.get_color(r_score)
            })
        return {"results": cve_list}
    except Exception as e:
        log.error(f"CVE Error: {e}")
        return {"results": [], "error": str(e)}

@app.get("/vuln/{cve_id}")
def get_vulnerability(cve_id: str, current_user: User = Depends(auth.get_current_user)):
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        vulnerabilities = data.get("vulnerabilities", [])
        if not vulnerabilities:
            raise HTTPException(status_code=404, detail="Vulnerability not found")
            
        item = vulnerabilities[0].get("cve", {})
        descriptions = item.get("descriptions", [])
        desc_text = next((d.get("value") for d in descriptions if d.get("lang") == "en"), "No description available.")
        
        metrics = item.get("metrics", {})
        cvss_score = 0.0
        cvss_severity = "N/A"
        for m_key in ["cvssMetricV31", "cvssMetricV30", "cvssMetricV2"]:
            m_list = metrics.get(m_key, [])
            if m_list:
                cvss_data = m_list[0].get("cvssData", {})
                cvss_score = cvss_data.get("baseScore", 0.0)
                cvss_severity = cvss_data.get("baseSeverity") or m_list[0].get("baseSeverity", "N/A")
                break
                
        mitigation = "Apply latest vendor patches. Monitor network traffic for anomalous behavior targeting this vulnerability."
        
        return {
            "id": cve_id,
            "description": desc_text,
            "cvss_score": cvss_score,
            "severity": str(cvss_severity).upper(),
            "mitigation": mitigation
        }
    except Exception as e:
        log.error(f"Vulnerability lookup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ScanRequest(BaseModel):
    code: str
    language: str = "auto"

@app.post("/scan")
def scan_code(req: ScanRequest, current_user: User = Depends(auth.get_current_user)):
    engine = get_engine()
    if not engine.llm:
        return {"success": False, "error": "LLM engine is unavailable on this deployment."}

    prompt = f"""You are a Senior Security Researcher. Analyze the code below for security vulnerabilities (SAST). 
Look for: OWASP Top 10, injection flaws, broken access control, hardcoded secrets, and cryptographic failures.

OUTPUT RULES:
- Return ONLY a JSON list of objects.
- Each object must have: "severity", "line", "vulnerability", "description", "fix".
- Severity must be one of: [Critical, High, Medium, Low].
- If no issues are found, return [].

CODE TO ANALYZE ({req.language}):
---
{req.code}
---
JSON OUTPUT:"""
    
    try:
        response = engine.llm.invoke([HumanMessage(content=prompt)])
        findings = safe_json_parse(response.content, fallback=[])
        return {"success": True, "findings": findings}
    except Exception as e:
        log.error(f"Scanning Error: {e}")
        return {"success": False, "error": f"AI Scanning service error: {str(e)}. Please ensure Ollama is available."}

@app.post("/classify")
def classify_threat(req: ClassifyRequest, current_user: User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    cls, conf = _classifier.predict(req.text)
    all_probs = _classifier.get_all_probs(req.text)
    
    severity = "High" if conf > 0.8 and cls in ["Malware", "Phishing"] else "Medium"
    
    threat_entry = ThreatLog(user_id=current_user.id, type=cls, severity=severity, source="classification_api")
    db.add(threat_entry)
    db.commit()
    
    return {"category": cls, "confidence": conf, "probabilities": all_probs}

@app.get("/history")
def get_history(current_user: User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    history = db.query(QueryHistory).filter(QueryHistory.user_id == current_user.id).order_by(QueryHistory.timestamp.desc()).all()
    return {"history": [{"id": h.id, "query": h.query, "response": h.response, "timestamp": h.timestamp} for h in history]}

@app.delete("/history/{history_id}")
def delete_history(history_id: int, current_user: User = Depends(auth.get_current_user), db: Session = Depends(database.get_db)):
    entry = db.query(QueryHistory).filter(QueryHistory.id == history_id, QueryHistory.user_id == current_user.id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="History entry not found")
    
    db.delete(entry)
    db.commit()
    return {"success": True, "message": "Entry deleted"}

@app.post("/report/generate")
def generate_report(req: ReportRequest, current_user: User = Depends(auth.get_current_user)):
    try:
        data = req.dict()
        pdf_buffer = report_generator.generate_cti_pdf(data)
        
        headers = {
            "Content-Disposition": "attachment; filename=CTI_Analysis_Report.pdf"
        }
        
        return StreamingResponse(
            pdf_buffer, 
            media_type="application/pdf", 
            headers=headers
        )
    except Exception as e:
        log.error(f"Report Generation Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
