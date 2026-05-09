"""
╔══════════════════════════════════════════════════════════════╗
║   CTI ANALYST PLATFORM — Professional SaaS Edition          ║
║   Cyber Threat Intelligence RAG Chatbot                      ║
╚══════════════════════════════════════════════════════════════╝
"""
import re
import io
import datetime
import streamlit as st
import json
import requests
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

class APIClient:
    @staticmethod
    def _handle_response(resp):
        try:
            if resp.status_code == 200:
                return resp.json()
            return {"error": f"API Error {resp.status_code}: {resp.text}"}
        except Exception as e:
            return {"error": f"JSON Parsing Error: {str(e)}"}

    @staticmethod
    def health_check():
        try:
            # Short timeout to avoid blocking UI
            return requests.get(f"{API_URL}/", timeout=2).json()
        except: return None

    @staticmethod
    def index_files(files):
        try:
            file_list = [("files", (f.name, f.getbuffer(), f.type)) for f in files]
            resp = requests.post(f"{API_URL}/index", files=file_list, timeout=180)
            return APIClient._handle_response(resp)
        except Exception as e:
            return {"error": f"Connection Error: {str(e)}"}

    @staticmethod
    def query(question):
        try:
            resp = requests.post(f"{API_URL}/query", json={"question": question}, timeout=180)
            return APIClient._handle_response(resp)
        except Exception as e:
            return {"error": f"Connection Error: {str(e)}"}

    @staticmethod
    def search_cve(query):
        try:
            resp = requests.get(f"{API_URL}/cve", params={"query": query}, timeout=15)
            return APIClient._handle_response(resp)
        except Exception as e:
            return {"error": f"Connection Error: {str(e)}"}

    @staticmethod
    def classify(text):
        try:
            resp = requests.post(f"{API_URL}/classify", json={"text": text}, timeout=10)
            return APIClient._handle_response(resp)
        except Exception as e:
            return {"error": f"Connection Error: {str(e)}"}

    @staticmethod
    def scan_code(code, lang="auto"):
        try:
            resp = requests.post(f"{API_URL}/scan", json={"code": code, "language": lang}, timeout=300)
            return APIClient._handle_response(resp)
        except Exception as e:
            return {"error": f"Connection Error: {str(e)}"}

class DocProxy:
    """Lightweight proxy for Document objects returned as dicts from API."""
    def __init__(self, data):
        self.page_content = data.get("page_content", "")
        self.metadata = data.get("metadata", {})

# ─── Page config MUST be first streamlit call ───────────────
def get_base64_logo():
    import base64
    logo_path = os.path.join(os.path.dirname(__file__), "../../assets/logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            return f"data:image/png;base64,{base64.b64encode(f.read()).decode()}"
    return None

LOGO_B64 = get_base64_logo()

st.set_page_config(
    page_title="CTI Analyst Platform",
    page_icon=os.path.join(os.path.dirname(__file__), "../../assets/logo.png") if os.path.exists(os.path.join(os.path.dirname(__file__), "../../assets/logo.png")) else "🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# FULL CUSTOM CSS — Dark Cyber + Glassmorphism
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* Professional Design Tokens */
:root {
    --bg-main:      #0f172a;
    --bg-surface:   #1e293b;
    --bg-sidebar:   #020617;
    --accent-primary: #6366f1;
    --accent-secondary: #0ea5e9;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --text-muted:    #64748b;
    --border:       #334155;
    --green:        #10b981;
    --red:          #ef4444;
    --yellow:       #f59e0b;
    --shadow:       0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    --shadow-hover: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

/* Global Layout */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-main) !important;
    background-image: radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.05) 0px, transparent 50%),
                      radial-gradient(at 50% 0%, rgba(14, 165, 233, 0.05) 0px, transparent 50%) !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Max Width Constraint for Content */
.block-container {
    max-width: 1100px !important;
    padding-top: 2rem !important;
    padding-bottom: 5rem !important;
    animation: fadeIn 0.4s ease-out;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
footer { visibility: hidden !important; }

/* Typography */
h1, h2, h3 {
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
    color: var(--text-primary) !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}

/* Base Components - Feature Cards */
.f-card {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: var(--shadow);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}
.f-card:hover {
    transform: translateY(-4px) scale(1.005);
    box-shadow: var(--shadow-hover);
    border-color: var(--accent-primary);
}

/* Simple Cards */
.m-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
}

.m-val {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--accent-secondary);
}
.m-lbl {
    font-size: 0.75rem;
    font-weight: 500;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}

/* Chat Styles */
.bbl-user {
    background: var(--accent-primary);
    color: white;
    border-radius: 12px 12px 0 12px;
    padding: 1rem 1.25rem;
    margin: 1rem 0 0.5rem auto;
    max-width: 85%;
    font-size: 0.95rem;
    line-height: 1.5;
    animation: fadeIn 0.3s ease-out forwards;
}
.bbl-ai {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    color: var(--text-primary);
    border-radius: 12px 12px 12px 0;
    padding: 1rem 1.25rem;
    margin: 1rem auto 0.5rem 0;
    max-width: 90%;
    font-size: 0.95rem;
    line-height: 1.6;
    animation: fadeIn 0.3s ease-out forwards;
}

.chunk-box {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}

/* Modern Pill Buttons */
.stButton > button, .stDownloadButton > button {
    background: var(--accent-primary) !important;
    color: white !important;
    border: 1px solid transparent !important;
    padding: 0.6rem 1.75rem !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
.stButton > button:hover {
    background: #4f46e5 !important;
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

/* Rounded Inputs */
[data-testid="stTextInput"] input, 
[data-testid="stTextArea"] textarea,
[data-testid="stChatInput"] textarea {
    background-color: rgba(0, 0, 0, 0.2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Section Dividers */
.cdiv {
    border: none;
    height: 1px;
    background: var(--border);
    margin: 2rem 0;
}

.stitle {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
}

/* Sidebar Navigation Refinement */
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    margin-bottom: 6px !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:hover {
    background: rgba(99, 102, 241, 0.05) !important;
    border-color: rgba(99, 102, 241, 0.2) !important;
    transform: translateX(4px);
}

/* Active Highlight for Radio Items */
[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked) {
    background: rgba(99, 102, 241, 0.12) !important;
    border-color: var(--accent-primary) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] label:has(input:checked) p {
    color: var(--accent-primary) !important;
    font-weight: 600 !important;
}

/* Indicators */
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.dot-on { background: var(--green); box-shadow: 0 0 8px var(--green); }
.dot-off { background: var(--text-muted); }

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.fade-in {
    animation: fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-main); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# IOC highlighting helpers
# ══════════════════════════════════════════════════════════════
_RE_URL    = re.compile(r'https?://[^\s\)\]\'\"<>]+')
_RE_IP     = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
_RE_DOMAIN = re.compile(r'\b(?:[a-zA-Z0-9\-]+\[?\.\]?)+(?:com|net|org|io|gov|edu|ru|cn|uk|onion)\b')
_RE_HASH   = re.compile(r'\b[a-fA-F0-9]{40}\b|\b[a-fA-F0-9]{64}\b')

def highlight_iocs(text: str) -> str:
    """Colour-code IOCs in AI response HTML."""
    ph = {}
    c  = [0]
    def rep(m, cls):
        k = f"__P{c[0]}__"; c[0] += 1
        ph[k] = f'<span class="ioc-{cls}">{m.group(0)}</span>'
        return k
    text = _RE_URL.sub(lambda m: rep(m, "url"), text)
    text = _RE_IP.sub(lambda m: rep(m, "ip"), text)
    text = _RE_DOMAIN.sub(lambda m: rep(m, "domain"), text)
    text = _RE_HASH.sub(lambda m: rep(m, "hash"), text)
    for k, v in ph.items():
        text = text.replace(k, v)
    return text


def confidence_score(response: dict, query: str) -> float:
    """Dynamic 0→1 confidence based on query type, retrieved context, and answer content."""
    docs   = response.get("context", [])
    answer = response.get("answer", "").lower()
    
    if not docs:
        return 0.0
    
    # 1. Base score from document count
    # Handle both Document objects and plain dictionaries from API
    scores = []
    for d in docs:
        metadata = d.get("metadata", {}) if isinstance(d, dict) else getattr(d, "metadata", {})
        score = metadata.get("score")
        if score is not None:
            scores.append(score)
            
    if scores:
        avg_sim = sum(scores) / len(scores)
        base = min(max(avg_sim, 0.3), 0.8)
    else:
        base = min(0.3 + (len(docs) * 0.12), 0.8)
    
    # 2. Query Analysis: Subjective vs Objective
    subjective_keywords = ["dangerous", "serious", "best", "should", "opinion", "risk level", "how bad", "think", "recommend"]
    query_lower = query.lower()
    is_subjective = any(word in query_lower for word in subjective_keywords)
    subjectivity_penalty = 0.35 if is_subjective else 0.0
    
    # 3. Answer Analysis: Uncertainty Detection
    uncertainty_keywords = ["might", "possibly", "unclear", "likely", "suggests", "maybe", "insufficient", "not explicitly"]
    uncertainty_count = sum(1 for word in uncertainty_keywords if word in answer)
    # Each uncertainty word reduces confidence by 0.1
    uncertainty_factor = max(0.5, 1.0 - (uncertainty_count * 0.1))
    
    # 4. Final Calculation
    # (Base + Boost) modulated by uncertainty, then penalised for subjectivity
    boost = 0.15 if not is_subjective else 0.05
    final_score = ((base + boost) * uncertainty_factor) - subjectivity_penalty
    
    # Ensure range [0.05, 0.98] to show some variation but avoid absolute 0/1
    return round(max(0.05, min(0.98, final_score)), 2)


def conf_label(score: float):
    if score >= 0.75: return "HIGH",   "dot-on",  "#00ff88"
    if score >= 0.40: return "MEDIUM", "dot-on",  "#ffd32a"
    return               "LOW",    "dot-off", "#ff4757"


# ══════════════════════════════════════════════════════════════
# PDF / TXT report generation
# ══════════════════════════════════════════════════════════════
def make_report(messages: list) -> tuple[bytes, str, str]:
    """Returns (bytes, filename, mime)."""
    ts = datetime.datetime.now()
    ts_str = ts.strftime("%Y-%m-%d %H:%M:%S")
    fname  = ts.strftime("CTI_Report_%Y%m%d_%H%M%S")

    # Try reportlab PDF
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch

        buf  = io.BytesIO()
        doc  = SimpleDocTemplate(buf, pagesize=letter,
                                 topMargin=.75*inch, bottomMargin=.75*inch)
        s    = getSampleStyleSheet()
        story = []

        t_style = ParagraphStyle("T", parent=s["Heading1"], fontSize=16,
                                 textColor=colors.HexColor("#6366f1"), spaceAfter=4)
        story.append(Paragraph("CTI Analyst — Session Report", t_style))
        story.append(Paragraph(f"Generated: {ts_str}", s["Normal"]))
        story.append(Spacer(1, .25*inch))

        for msg in messages:
            is_user = msg["role"] == "user"
            role_c  = "#3d7eff" if is_user else "#00ff88"
            role_lbl = "USER QUERY" if is_user else "AI RESPONSE"
            conf_txt = ""
            if not is_user and "confidence" in msg:
                conf_txt = f"  |  Confidence: {int(msg['confidence']*100)}%"
            h = ParagraphStyle("H", fontSize=9,
                               textColor=colors.HexColor(role_c),
                               spaceBefore=10, spaceAfter=3)
            story.append(Paragraph(f"▶ {role_lbl}{conf_txt}", h))
            clean = re.sub(r"<[^>]*>", "", msg["content"])
            story.append(Paragraph(clean, s["Normal"]))

        doc.build(story)
        return buf.getvalue(), fname + ".pdf", "application/pdf"

    except ImportError:
        lines = [f"CTI ANALYST SESSION REPORT\nGenerated: {ts_str}\n{'='*70}\n"]
        for m in messages:
            role = "USER" if m["role"] == "user" else "AI"
            conf = f" [Conf: {int(m.get('confidence',0)*100)}%]" if m["role"] == "assistant" and "confidence" in m else ""
            lines.append(f"\n[{role}]{conf}\n{'-'*60}\n{re.sub(r'<[^>]*>','',m['content'])}\n")
        return "\n".join(lines).encode("utf-8"), fname + ".txt", "text/plain"


# ══════════════════════════════════════════════════════════════
# Session State
# ══════════════════════════════════════════════════════════════
def _init():
    defs = dict(
        rag_engine_active=False,
        messages=[],
        chunks_count=0,
        files_loaded=[],
        upload_status=None,
        upload_msg="",
        query_history=[],
        selected_recall=None
    )
    for k, v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Check backend health
    health = APIClient.health_check()
    st.session_state.rag_engine_active = health is not None

_init()

# ─── Navigation ──────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="stitle">🧭 Navigation</div>', unsafe_allow_html=True)
    view_mode = st.radio(
        "Select View",
        ["Analyst Chat", "OWASP 2025 Dashboard", "Threat Actors", "CVE Intel Tool", "Code Scanner (Sim)", "🧠 Threat Engine"],
        label_visibility="collapsed"
    )
    
    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="stitle">👤 Role Access</div>', unsafe_allow_html=True)
    role = st.selectbox("Current Role", ["CISO", "SOC Analyst", "Threat Hunter"], index=1)
    
    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    st.markdown('<div class="stitle">📜 Session History</div>', unsafe_allow_html=True)
    if not st.session_state.query_history:
        st.caption("No queries recorded yet.")
    else:
        for i, item in enumerate(st.session_state.query_history):
            # Shorten label
            label = item["query"][:28] + "..." if len(item["query"]) > 30 else item["query"]
            if st.button(f"⏱️ {item['timestamp']} | {label}", key=f"hist_{i}", use_container_width=True):
                st.session_state.selected_recall = item
    
    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

engine_ok = st.session_state.rag_engine_active and st.session_state.chunks_count > 0


# ══════════════════════════════════════════════════════════════
# TOP HEADER (sticky via CSS position fixed workaround)
# ══════════════════════════════════════════════════════════════
dot_cls  = "dot-on"  if engine_ok else "dot-off"
status   = "ACTIVE"  if engine_ok else "STANDBY"

# Define logo components outside f-string to avoid backslash issues in older Python versions
header_logo_html = f'<img src="{LOGO_B64}" style="height:32px;">' if LOGO_B64 else '<span style="font-size:1.5rem;">🛡️</span>'

st.markdown(f"""
<div style="
    width:100%; padding:1rem 2rem;
    background: var(--bg-surface);
    border-bottom: 1px solid var(--border);
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:2rem;
">
    <div style="display:flex;align-items:center;gap:12px;">
        {header_logo_html}
        <span style="
            font-size:1rem; font-weight:700;
            color: var(--text-primary); letter-spacing:2px;
        ">CTI ANALYST PLATFORM</span>
    </div>
    <div style="display:flex;align-items:center;gap:14px;">
        <span style="font-size:.75rem;color:var(--text-muted);font-weight:500;">
            RAG • FAISS • Ollama
        </span>
        <span style="
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid var(--accent-primary);
            border-radius: 999px; padding:4px 12px;
            font-size:.7rem; font-weight:600; color: var(--accent-primary);
        ">
            <span class="dot {dot_cls}"></span> {status}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# SIDEBAR — Threat Intel Control Panel
# ══════════════════════════════════════════════════════════════
sidebar_logo_html = f'<img src="{LOGO_B64}" style="height:64px;">' if LOGO_B64 else '<div style="font-size:1.75rem;">🛡️</div>'

with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:1rem 0;">
        <div style="margin-bottom:0.5rem;">
            {sidebar_logo_html}
        </div>
        <div style="font-size:.7rem;
                    color: var(--accent-secondary); font-weight:700; letter-spacing:2px;">
            SEC-OPS CONTROL PANEL
        </div>
    </div>
    <div class="cdiv"></div>
    """, unsafe_allow_html=True)

    # Metrics
    st.markdown('<div class="stitle">⚙ System Status</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="m-card">
            <div class="m-val">{st.session_state.chunks_count}</div>
            <div class="m-lbl">Chunks</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="m-card">
            <div class="m-val">{len(st.session_state.files_loaded)}</div>
            <div class="m-lbl">Reports</div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="model-box">
        <div class="lbl">LLM ENGINE</div>
        <div class="val">{os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")}</div>
        <div class="lbl" style="margin-top:8px;">EMBEDDINGS</div>
        <div class="val2">{os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")}</div>
        <div class="lbl" style="margin-top:8px;">VECTOR STORE</div>
        <div class="val">FAISS</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    # Upload section
    st.markdown('<div class="stitle">📂 Document Repository</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Upload CTI Reports",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded:
        st.markdown(f"""
        <div class="upst upst-wait">
            ⏳ {len(uploaded)} file(s) ready — click PROCESS
        </div>""", unsafe_allow_html=True)

    if st.button("⚡  PROCESS DOCUMENTS", use_container_width=True):
        if uploaded:
            with st.spinner("🔄 Building vector index on backend…"):
                try:
                    resp = APIClient.index_files(uploaded)
                    if resp.get("success"):
                        st.session_state.chunks_count = resp.get("chunks", 0)
                        st.session_state.files_loaded = [f.name for f in uploaded]
                        st.session_state.upload_status = "ok"
                        st.session_state.upload_msg = resp.get("message", "Files indexed.")
                        st.rerun()
                    else:
                        st.session_state.upload_status = "err"
                        st.session_state.upload_msg = resp.get("detail", "Indexing failed.")
                        st.rerun()
                except Exception as ex:
                    st.session_state.upload_status = "err"
                    st.session_state.upload_msg = f"Backend Error: {str(ex)}"
                    st.rerun()
        else:
            st.warning("Upload files first.")

    # Show upload result
    if st.session_state.upload_status == "ok":
        st.markdown(f"""
        <div class="upst upst-ok">✅ {st.session_state.upload_msg}</div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="stitle" style="margin-top:10px;">📌 Loaded Files</div>',
                    unsafe_allow_html=True)
        for fn in st.session_state.files_loaded:
            st.markdown(
                f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.7rem;'
                f'color:#00ff88;padding:2px 0;">› {fn}</div>',
                unsafe_allow_html=True)
    elif st.session_state.upload_status == "err":
        st.markdown(f"""
        <div class="upst upst-err">❌ {st.session_state.upload_msg}</div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

    # Actions
    st.markdown('<div class="stitle">🗂 Session Actions</div>', unsafe_allow_html=True)
    if st.button("🗑  CLEAR CHAT", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.session_state.messages:
        data, fname, mime = make_report(st.session_state.messages)
        st.download_button("📥  EXPORT REPORT", data=data,
                           file_name=fname, mime=mime,
                           use_container_width=True)

    num_q = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown(
        f'<div style="text-align:center;margin-top:14px;font-family:\'JetBrains Mono\','
        f'monospace;font-size:.65rem;color:#2d3a52;">{num_q} queries this session</div>',
        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# OWASP DASHBOARD RENDERER
# ══════════════════════════════════════════════════════════════
def render_owasp_dashboard():
    st.markdown('<div class="f-card">', unsafe_allow_html=True)
    st.markdown("""
    <div style="background: var(--bg-surface); border-bottom:1px solid var(--border); 
                padding-bottom:1.5rem; margin-bottom:2rem;">
        <h2 style="color: var(--accent-secondary); margin:0; font-size:1.5rem;">
            OWASP TOP 10 : 2025
        </h2>
        <p style="color: var(--text-secondary); font-size:0.9rem; margin-top:0.5rem;">
            Strategic Vulnerability Intelligence Dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        owasp_path = os.path.join(os.path.dirname(__file__), "database", "owasp_2025.json")
        if not os.path.exists(owasp_path):
            st.warning("⚠️ OWASP 2025 data file not found.")
            return

        with open(owasp_path, "r") as f:
            owasp_data = json.load(f)
        
        # Heatmap / Summary Grid
        cols = st.columns(5)
        for i, item in enumerate(owasp_data):
            with cols[i % 5]:
                st.markdown(f"""
                <div class="m-card" style="margin-bottom:15px; cursor:pointer;">
                    <div style="font-size:0.7rem; color:var(--text-muted);">{item['id']}</div>
                    <div style="color:var(--accent-secondary); font-weight:bold; font-size:0.8rem; height:40px;">{item['title']}</div>
                    <div class="m-val" style="font-size:1.1rem;">{item['risk_score']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="cdiv"></div>', unsafe_allow_html=True)

        # Tabs for details
        tab_titles = [item['id'] for item in owasp_data]
        tabs = st.tabs(tab_titles)

        for i, tab in enumerate(tabs):
            item = owasp_data[i]
            with tab:
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.markdown(f"### {item['id']} {item['title']}")
                    st.write(item['description'])
                    
                    st.markdown("#### 💡 Real World Example")
                    st.info(item['real_world_example'])
                    
                    st.markdown("#### 🛡️ Prevention & Defensive Strategy")
                    st.success(item['prevention'])
                    st.markdown(f"**Strategic Approach:** {item['defensive_strategy']}")
                
                with c2:
                    st.markdown(f"""
                    <div class="model-box">
                        <div class="lbl">SEVERITY</div><div class="val" style="color:{'#ff4757' if item['severity'] == 'Critical' else '#ff4757' if item['severity'] == 'High' else '#ffd32a'}">{item['severity']}</div>
                        <div class="lbl">THREAT LEVEL</div><div class="val">{item['threat_level']}</div>
                        <div class="lbl">EXPLOIT LIKELIHOOD</div><div class="val2">{item['exploit_likelihood']}</div>
                        <div class="lbl">ATTACK VECTOR</div><div class="val">{item['attack_vector']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("#### 📝 Secure Coding Checklist")
                    for check in item['secure_coding_checklist']:
                        st.markdown(f"- [ ] {check}")

                st.markdown("---")
                with st.expander("🔍 Deep Dive: Real Attack Scenario & MITRE Mapping"):
                    st.warning(f"**Scenario:** {item['real_attack_scenario']}")
                    st.markdown(f"**MITRE ATT&CK Techniques:** {', '.join(item['related_mitre_techniques'])}")

    except Exception as e:
        st.error(f"Error loading OWASP data: {e}")

    # ─── Analytics Section ──────────────────────────────────
    st.markdown("### 📊 Vulnerability Analytics")
    try:
        df = pd.DataFrame(owasp_data)
        
        c1, c2 = st.columns(2)
        with c1:
            # Heatmap / Scatter
            fig = px.scatter(df, x="exploit_likelihood", y="risk_score",
                             size="risk_score", color="severity",
                             hover_name="title", text="id",
                             title="Risk Score vs Exploit Likelihood",
                             color_discrete_map={"Critical": "#ff4757", "High": "#ffa502", "Medium": "#ffd32a"},
                             template="plotly_dark")
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            # Bar chart of risk scores
            fig2 = px.bar(df, x="id", y="risk_score", color="severity",
                          title="Threat Magnitude by Category",
                          color_discrete_map={"Critical": "#ff4757", "High": "#ffa502", "Medium": "#ffd32a"},
                          template="plotly_dark")
            fig2.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)
            
    except Exception as e:
        st.write(f"Analytics error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# THREAT ACTOR RENDERER
# ══════════════════════════════════════════════════════════════
def render_threat_actors():
    st.markdown('<div class="f-card">', unsafe_allow_html=True)
    st.markdown('<div class="stitle">🕵️ Threat Actor Profiling</div>', unsafe_allow_html=True)
    
    try:
        actors_path = os.path.join(os.path.dirname(__file__), "database", "threat_actors.json")
        if not os.path.exists(actors_path):
            st.warning("⚠️ Threat Actors data file not found.")
            return

        with open(actors_path, "r") as f:
            actors = json.load(f)
        
        for actor in actors:
            with st.expander(f"🛡️ {actor['name']} ({actor['country']})"):
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown(f"**Origin:** `{actor['country']}`")
                    st.markdown("**Targets:**")
                    for ind in actor['target_industries']:
                        st.markdown(f"- {ind}")
                with c2:
                    st.markdown(f"**Recent Campaigns:** {', '.join(actor['recent_campaigns'])}")
                    st.markdown("**Core TTPs:**")
                    st.info(", ".join(actor['ttps']))
                
                cols = st.columns(len(actor['mitre_techniques']))
                for i, tech in enumerate(actor['mitre_techniques']):
                    with cols[i]:
                        st.markdown(f'<div class="m-card" style="text-align:center; background:rgba(255,255,255,0.03);">{tech}</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading actors: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CVE INTEL RENDERER (Simulated)
# ══════════════════════════════════════════════════════════════

def render_cve_tool():
    st.markdown('<div class="f-card">', unsafe_allow_html=True)
    st.markdown('<div class="stitle">🔍 CVE Live Intelligence</div>', unsafe_allow_html=True)
    query = st.text_input("Search CVE database (e.g. 'Log4j', 'Exchange', 'Injection')", label_visibility="collapsed")
    
    # We always call search_cve, backend now handles empty query as "latest"
    status_msg = f"📡 Querying NVD for: **{query}**..." if query else "📡 Fetching Latest Vulnerabilities..."
    
    with st.spinner(status_msg):
        try:
            resp = APIClient.search_cve(query)
            cves = resp.get("results", [])
            error = resp.get("error")
        except Exception as e:
            cves = []
            error = f"Connection Error: {str(e)}"
    
    # Handle Offline Backend or Connection Errors
    if error:
        is_conn_err = "Connection Error" in error or "10061" in error
        err_icon = "🔌" if is_conn_err else "❌"
        err_title = "Backend Service Offline" if is_conn_err else "API Error"
        
        st.markdown(f"""
        <div style="background:rgba(255,71,87,.1); border:1px solid rgba(255,71,87,.3); 
                    border-radius:12px; padding:20px; color:#ff4757; font-family:'Inter',sans-serif;">
            <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
                <span style="font-size:1.5rem;">{err_icon}</span>
                <b style="font-size:1.1rem;">{err_title}</b>
            </div>
            <div style="font-size:0.9rem; line-height:1.6; color:var(--text-primary);">
                {error}
            </div>
            {"<div style='margin-top:15px; padding:12px; background:rgba(255,255,255,0.05); border-radius:8px; font-size:0.85rem; color:var(--text-secondary); border:1px solid rgba(255,255,255,0.1);'>"
              "<b>How to fix:</b> Run the following command in a new terminal to start the intelligence engine:<br>"
              "<code style='color:var(--accent-secondary); background:rgba(0,0,0,0.3); padding:2px 6px; border-radius:4px;'>uvicorn main:app --reload</code>"
              "</div>" if is_conn_err else ""}
        </div>
        """, unsafe_allow_html=True)
        
        if "Rate limited" in error or "403" in error:
            st.caption("NVD API 2.0 has strict rate limits. Please wait 30 seconds and refresh.")
        return

    if not cves:
        if query:
            st.warning(f"No results found for '{query}'. Try a broader keyword (e.g., 'Cisco' instead of a specific version).")
        else:
            st.info("No recent CVEs available. The NVD service might be experiencing high traffic.")
    else:
        lbl = f"Search Results: **{query}**" if query else "Latest Global Vulnerabilities"
        st.markdown(f'<div style="color:var(--text-muted); font-size:0.75rem; margin-bottom:12px; font-weight:600;">{lbl.upper()}</div>', unsafe_allow_html=True)
        
        for cve in cves:
            r_color = cve.get('risk_color', '#4a5a7a')
            r_label = cve.get('risk_label', 'N/A')
            r_score = int(cve.get('risk_score', 0))
            
            st.markdown(f"""
            <div class="chunk-box" style="border-left: 4px solid {r_color}; background: var(--bg-surface);">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <b style="color:var(--accent-secondary); font-size:1.1rem;">{cve['id']}</b>
                        <span style="color:var(--text-muted); font-size:0.75rem; margin-left:10px;">CVSS: {cve['score']} ({cve['severity']})</span>
                    </div>
                    <div style="background:{r_color}11; color:{r_color}; border:1px solid {r_color}33; 
                                padding:2px 10px; border-radius:4px; font-size:0.7rem; font-weight:700;">
                        RISK: {r_label} ({r_score})
                    </div>
                </div>
                <div style="color:var(--text-secondary); font-size:0.87rem; margin-top:10px; line-height:1.6;">{cve['desc']}</div>
                <div style="display:flex; justify-content:flex-end; margin-top:8px;">
                    <a href="https://nvd.nist.gov/vuln/detail/{cve['id']}" target="_blank" style="text-decoration:none; color:var(--accent-secondary); font-size:0.65rem; font-family:'JetBrains Mono',monospace;">
                        VIEW NVD SOURCE ↗
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# CODE SCANNER RENDERER (SOC Mode Simulation)
# ══════════════════════════════════════════════════════════════
def render_code_scanner():
    st.markdown('<div class="f-card">', unsafe_allow_html=True)
    st.markdown('<div class="stitle">🛡️ Static Analysis Sandbox (SAST)</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: var(--bg-surface); border:1px solid var(--border); 
                border-radius:12px; padding:15px; margin-bottom:20px;">
        <p style="color: var(--text-secondary); font-size:0.85rem; margin:0;">
            Paste a code snippet (Python, JS, Go, etc.) to analyze for security vulnerabilities using the LLM engine.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns([3, 1])
    with c1:
        lang = st.selectbox("Language", ["Auto-detect", "Python", "Javascript", "Java", "C++", "Go", "Solidity"], label_visibility="collapsed")
    
    code_input = st.text_area("Paste source code here:", height=300, 
                              placeholder="# Example: Hardcoded credentials\nAPI_KEY = 'SK-1234567890'\n\ndef query_db(user_id):\n    # Example: SQL Injection\n    query = f'SELECT * FROM users WHERE id = {user_id}'",
                              help="The LLM will analyze this code for OWASP Top 10 and other security flaws.")
    
    if st.button("🚀  LAUNCH SECURITY SCAN", use_container_width=True):
        if not code_input.strip():
            st.warning("Please enter some code to analyze.")
            return

        with st.spinner("🤖 SOC Engine analyzing code patterns..."):
            try:
                resp = APIClient.scan_code(code_input, lang)
                if resp.get("success"):
                    findings = resp.get("findings", [])
                    
                    if not findings:
                        st.success("✅ No critical security issues identified in this snippet.")
                    else:
                        # Summary Dashboard
                        st.markdown('<div class="stitle" style="margin-top:25px;">📊 Vulnerability Summary</div>', unsafe_allow_html=True)
                        
                        # Count severities
                        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
                        for f in findings:
                            sev = f.get("severity", "Low")
                            if sev in counts: counts[sev] += 1
                        
                        cols = st.columns(4)
                        sev_colors = {"Critical": "#ff4757", "High": "#ffa502", "Medium": "#ffd32a", "Low": "#3d7eff"}
                        
                        for i, (label, count) in enumerate(counts.items()):
                            with cols[i]:
                                st.markdown(f"""
                                <div class="m-card" style="border-color:{sev_colors[label]}44;">
                                    <div class="m-val" style="color:{sev_colors[label]};">{count}</div>
                                    <div class="m-lbl">{label}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Detailed Findings
                        st.markdown('<div class="stitle" style="margin-top:25px;">🔎 Detailed Findings</div>', unsafe_allow_html=True)
                        
                        for i, f in enumerate(findings):
                            sev = f.get("severity", "Medium")
                            color = sev_colors.get(sev, "#6366f1")
                            
                            with st.expander(f"[{sev.upper()}] {f['vulnerability']} — Line {f.get('line', '?')}", expanded=True):
                                st.markdown(f"""
                                <div style="padding:5px 0;">
                                    <div style="font-size:0.85rem; color:var(--text-secondary); line-height:1.6; margin-bottom:12px;">
                                        {f['description']}
                                    </div>
                                    <div style="background:rgba(0,0,0,0.2); border:1px solid {color}44; border-radius:12px; padding:1.5rem;">
                                        <div style="color:{color}; font-size:0.75rem; margin-bottom:8px; font-weight:700;">🛡️ PROPOSED REMEDIATION</div>
                                        <div style="color:var(--text-primary); font-family:'JetBrains+Mono', monospace; font-size:0.85rem; line-height:1.5;">{f['fix']}</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                else:
                    st.error(f"Scan failed: {resp.get('error', 'Unknown backend error')}")
            except Exception as e:
                st.error(f"Frontend connection error: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# THREAT ENGINE RENDERER (ML Classifier)
# ══════════════════════════════════════════════════════════════
def render_threat_engine():
    st.markdown('<div class="f-card">', unsafe_allow_html=True)
    st.markdown('<div class="stitle">🧠 Predictive Threat Classification (ML)</div>', unsafe_allow_html=True)
    st.write("Analyze suspicious snippets using our probabilistic Naive Bayes engine.")
    
    text_input = st.text_area("Input log entry, email snippet, or report text:", height=150, 
                              placeholder="e.g., Executing powershell -enc BASE64... or Your files have been encrypted...")
    
    if st.button("🚀  ANALYZE THREAT", use_container_width=True):
        if text_input:
            with st.spinner("🤖 Classifier thinking..."):
                resp = APIClient.classify(text_input)
                cls = resp.get("category", "unknown")
                conf = resp.get("confidence", 0.0)
                all_probs = resp.get("probabilities", {})
                
            # Styling based on category
            colors = {
                "phishing": "#ffd32a",
                "malware": "#00ff88",
                "ransomware": "#ff4757",
                "benign": "#4a5a7a"
            }
            main_color = colors.get(cls, "var(--accent-primary)")
            
            st.markdown(f"""
            <div style="background: var(--bg-main); border:1px solid {main_color}44; border-radius:12px; padding:2rem; margin-top:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <div style="color:var(--text-muted); font-size:0.7rem; font-weight:700; letter-spacing:1px;">PREDICTED THREAT CATEGORY</div>
                        <div style="color:{main_color}; font-size:2rem; font-weight:700; text-transform:uppercase;">{cls}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="color:var(--text-muted); font-size:0.7rem; font-weight:700; letter-spacing:1px;">CONFIDENCE LEVEL</div>
                        <div style="color:{main_color}; font-size:1.8rem; font-weight:700;">{int(conf*100)}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Probability Breakdown
            st.markdown('<div class="stitle" style="margin-top:25px;">📊 Probability Breakdown</div>', unsafe_allow_html=True)
            for cat, prob in all_probs.items():
                p_pct = int(prob * 100)
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--text-muted); margin-bottom:4px;">
                        <span style="font-weight:600;">{cat.upper()}</span>
                        <span>{p_pct}%</span>
                    </div>
                    <div style="background:rgba(255,255,255,0.05); height:6px; border-radius:999px; width:100%;">
                        <div style="background:{colors.get(cat, 'var(--accent-primary)')}; height:100%; width:{p_pct}%; border-radius:999px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.warning("Please enter text to analyze.")
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# MAIN ROUTING
# ══════════════════════════════════════════════════════════════
if view_mode == "OWASP 2025 Dashboard":
    render_owasp_dashboard()
elif view_mode == "Threat Actors":
    render_threat_actors()
elif view_mode == "CVE Intel Tool":
    render_cve_tool()
elif view_mode == "Code Scanner (Sim)":
    render_code_scanner()
elif view_mode == "🧠 Threat Engine":
    render_threat_engine()
else:
    # ══════════════════════════════════════════════════════════════
    # RECALL VIEW (If user clicked a history item)
    # ══════════════════════════════════════════════════════════════
    if st.session_state.selected_recall:
        recall = st.session_state.selected_recall
        with st.container():
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.1); border:1px solid var(--yellow); border-radius:12px; padding:2rem; margin-bottom:2rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem;">
                    <div style="color:var(--yellow); font-size:0.75rem; font-weight:700; letter-spacing:1px;">
                        📜 HISTORICAL RECALL ( {recall['timestamp']} )
                    </div>
                    <button onclick="window.location.reload();" style="background:none; border:none; color:var(--text-muted); cursor:pointer; font-size:1.2rem;">×</button>
                </div>
                <div style="color:var(--text-muted); font-size:0.85rem; margin-bottom:0.5rem;"><b>Q:</b> {recall['query']}</div>
                <div style="color:var(--text-primary); font-size:0.95rem; line-height:1.7;">{highlight_iocs(recall['answer'])}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Close Recall", use_container_width=True):
                st.session_state.selected_recall = None
                st.rerun()

    # Existing Chat Logic
    if not st.session_state.messages:
        st.markdown('<div class="f-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; padding:2rem 1rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">🔍</div>
            <div style="font-size:1.25rem; font-weight:700;
                        color: var(--text-primary); letter-spacing:2px; margin-bottom:1rem;">
                CYBER THREAT INTELLIGENCE ENGINE
            </div>
            <div style="color: var(--text-secondary); font-size:0.95rem; max-width:600px;
                        margin:0 auto; line-height:1.7;">
                Upload threat reports (PDF / TXT) via the sidebar, then ask anything about
                <b style="color:var(--accent-secondary);">APTs</b>,
                <b style="color:var(--accent-secondary);">IOCs</b>,
                <b style="color:var(--accent-secondary);">TTPs</b>, malware, or campaigns.
                IOCs are auto-highlighted in every response.
            </div>
            <div style="display:flex; justify-content:center; gap:1rem; flex-wrap:wrap; margin-top:2rem;">
                <span style="background: rgba(99, 102, 241, 0.1); border:1px solid var(--accent-primary);
                             border-radius:999px; padding:6px 16px; font-size:0.75rem; color: var(--accent-primary); font-weight:600;">
                    💡 "What IOCs are linked to APT29?"
                </span>
                <span style="background: rgba(16, 185, 129, 0.1); border: 1px solid var(--green);
                             border-radius:999px; padding:6px 16px; font-size:0.75rem; color: var(--green); font-weight:600;">
                    💡 "Summarise the attack vector used."
                </span>
                <span style="background: rgba(14, 165, 233, 0.1); border: 1px solid var(--accent-secondary);
                             border-radius:999px; padding:6px 16px; font-size:0.75rem; color: var(--accent-secondary); font-weight:600;">
                    💡 "What malware family was deployed?"
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


    # ══════════════════════════════════════════════════════════════
    # CHAT HISTORY — render all previous messages
    # ══════════════════════════════════════════════════════════════
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="bbl-user-tag">👤 YOU</div>
            <div class="bbl-user">{msg['content']}</div>
            """, unsafe_allow_html=True)
        else:
            hi = highlight_iocs(msg["content"])
            st.markdown(f"""
            <div class="bbl-ai-tag">🛡️ CTI ANALYST AI</div>
            <div class="bbl-ai">{hi}</div>
            """, unsafe_allow_html=True)

            # Confidence bar
            if "confidence" in msg:
                sc   = msg["confidence"]
                lbl, _, clr = conf_label(sc)
                pct  = int(sc * 100)
                st.markdown(f"""
                <div class="conf-row">
                    <span style="font-family:'JetBrains Mono',monospace;font-size:.62rem;color:#4a5a7a;">
                        CONFIDENCE
                    </span>
                    <div class="conf-track">
                        <div class="conf-fill" style="width:{pct}%"></div>
                    </div>
                    <span class="conf-lbl" style="color:{clr};">{pct}% · {lbl}</span>
                </div>
                """, unsafe_allow_html=True)

            # IOC Discovery Panel (Phase 2)
            if msg.get("iocs") and any(msg["iocs"].values()):
                with st.expander("🔎 Extracted Indicators of Compromise (SOC Alert)"):
                    cols = st.columns(3)
                    iocs = msg["iocs"]
                    with cols[0]:
                        if iocs.get("ips"): st.markdown("**IPs:**\n- " + "\n- ".join(iocs["ips"]))
                        if iocs.get("domains"): st.markdown("**Domains:**\n- " + "\n- ".join(iocs["domains"]))
                    with cols[1]:
                        if iocs.get("hashes"): st.markdown("**Hashes:**\n- " + "\n- ".join(iocs["hashes"]))
                        if iocs.get("cves"): st.markdown("**CVEs:**\n- " + "\n- ".join(iocs["cves"]))
                    if iocs.get("urls"): st.markdown("**Resources:**\n- " + "\n- ".join(iocs["urls"]))
                    if iocs.get("emails"): st.markdown("**Emails:**\n- " + "\n- ".join(iocs["emails"]))

            # 📅 Threat Timeline (Phase 2)
            if msg.get("timeline"):
                with st.expander("📅 Attack Timeline Visualization"):
                    t_df = pd.DataFrame(msg["timeline"])
                    if not t_df.empty:
                        for _, row in t_df.iterrows():
                            st.markdown(f"**{row['date']}**: {row['event']}")
                        try:
                            fig = px.scatter(t_df, x="date", y=[1]*len(t_df), text="event", 
                                          title="Event Sequence", height=300, template="plotly_dark")
                            fig.update_traces(textposition="top center", marker=dict(size=12, color="#00d4ff"))
                            fig.update_yaxes(visible=False, showgrid=False, zeroline=False)
                            st.plotly_chart(fig, use_container_width=True)
                        except Exception: pass

            # RAG Evaluation Metrics (History)
            met = msg.get("metrics")
            if met:
                c_sc = int(met.get("avg_context_score", 0) * 100)
                a_sc = int(met.get("answer_relevancy", 0) * 100)
                r_lt = met.get("retrieval_latency", 0)
                g_lt = met.get("generation_latency", 0)
                
                st.markdown(f"""
                <div style="display:flex; gap:15px; margin-top:5px; padding:5px 10px; 
                            background:rgba(255,255,255,0.02); border-radius:4px; border:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.65rem; color:#4a5a7a;">
                        <span style="color:#8090aa;">CONTEXT:</span> <span style="color:#00d4ff;">{c_sc}%</span>
                    </div>
                    <div style="font-size:0.65rem; color:#4a5a7a; border-left:1px solid rgba(255,255,255,0.1); padding-left:10px;">
                        <span style="color:#8090aa;">RELV:</span> <span style="color:#ffd32a;">{a_sc}%</span>
                    </div>
                    <div style="font-size:0.65rem; color:#4a5a7a; border-left:1px solid rgba(255,255,255,0.1); padding-left:10px;">
                        <span style="color:#8090aa;">LATENCY:</span> <span style="color:#00ff88;">{r_lt}s / {g_lt}s</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Source chunks expander
            if msg.get("sources"):
                with st.expander(f"📄 Evidence — {len(msg['sources'])} retrieved chunk(s)", expanded=False):
                    for i, doc in enumerate(msg["sources"]):
                        pg   = doc.metadata.get("page", "—")
                        src  = os.path.basename(doc.metadata.get("source", "unknown"))
                        score = doc.metadata.get("score")
                        score_tag = f'<span style="color:#ffd32a;margin-left:10px;font-size:0.75rem;">RELEVANCE: {score:.2f}</span>' if score else ""
                        
                        st.markdown(f"""
                        <div class="chunk-box">
                            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                                <span style="color:#00d4ff; font-weight:bold; font-size:0.8rem;">CHUNK {i+1}</span>
                                <span style="color:#4a5a7a; font-size:0.75rem;">{src} (p. {pg}){score_tag}</span>
                            </div>
                            <div style="color:#8090aa; line-height:1.5; font-size:0.85rem;">{doc.page_content[:450]}…</div>
                        </div>
                        """, unsafe_allow_html=True)


    # CHAT INPUT
    # ══════════════════════════════════════════════════════════════
    hint = ("Ask about threat actors, IOCs, TTPs, malware families..."
            if engine_ok
            else "⚠️  Process documents first using the sidebar →")

    if prompt := st.chat_input(hint):
        # Store & display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.markdown(f"""
        <div class="bbl-user-tag">👤 YOU</div>
        <div class="bbl-user">{prompt}</div>
        """, unsafe_allow_html=True)

        if engine_ok:
            with st.spinner("🔎  Retrieving threat intelligence…"):
                try:
                    resp    = APIClient.query(prompt)
                    answer  = resp.get("answer", "No response generated.")
                    sources = [DocProxy(d) for d in resp.get("context", [])]
                    iocs    = resp.get("iocs", {})
                    sc      = confidence_score(resp, prompt)

                    # Display AI bubble
                    hi = highlight_iocs(answer)
                    st.markdown(f"""
                    <div class="bbl-ai-tag">🛡️ CTI ANALYST AI</div>
                    <div class="bbl-ai">{hi}</div>
                    """, unsafe_allow_html=True)

                    # Confidence & Risk row
                    lbl_c, _, clr_c = conf_label(sc)
                    pct_c = int(sc * 100)
                    
                    risk = resp.get("risk", {"score": 0, "label": "N/A", "color": "#4a5a7a"})
                    
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:12px;">
                        <div class="conf-row" style="margin-bottom:0;">
                            <span style="font-family:'JetBrains Mono',monospace;font-size:.62rem;color:#4a5a7a;">
                                CONFIDENCE
                            </span>
                            <div class="conf-track">
                                <div class="conf-fill" style="width:{pct_c}%"></div>
                            </div>
                            <span class="conf-lbl" style="color:{clr_c};">{pct_c}% · {lbl_c}</span>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-family:'JetBrains Mono',monospace;font-size:.62rem;color:#4a5a7a;display:block;margin-bottom:4px;">
                                THREAT RISK
                            </span>
                            <span style="background:{risk['color']}22; color:{risk['color']}; border:1px solid {risk['color']}44; 
                                         padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:700; font-family:'JetBrains Mono',monospace;">
                                {risk['label']} ({int(risk['score'])})
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # IOC Discovery Panel
                    if iocs and any(iocs.values()):
                        with st.expander("🔎 Extracted Indicators of Compromise (SOC Alert)", expanded=True):
                            cols = st.columns(3)
                            with cols[0]:
                                if iocs.get("ips"): st.markdown("**IPs:**\n- " + "\n- ".join(iocs["ips"]))
                                if iocs.get("domains"): st.markdown("**Domains:**\n- " + "\n- ".join(iocs["domains"]))
                            with cols[1]:
                                if iocs.get("hashes"): st.markdown("**Hashes:**\n- " + "\n- ".join(iocs["hashes"]))
                                if iocs.get("cves"): st.markdown("**CVEs:**\n- " + "\n- ".join(iocs["cves"]))
                            with cols[2]:
                                if iocs.get("urls"): st.markdown("**Resources:**\n- " + "\n- ".join(iocs["urls"]))
                                if iocs.get("emails"): st.markdown("**Emails:**\n- " + "\n- ".join(iocs["emails"]))
                    
                    # Timeline Panel (New Response)
                    if resp.get("timeline"):
                        with st.expander("📅 Attack Timeline Visualization", expanded=True):
                            t_df = pd.DataFrame(resp["timeline"])
                            if not t_df.empty:
                                for _, row in t_df.iterrows():
                                    st.markdown(f"**{row['date']}**: {row['event']}")

                    # Source expander
                    if sources:
                        with st.expander(f"📄 Evidence — {len(sources)} retrieved chunk(s)", expanded=False):
                            for i, doc in enumerate(sources):
                                pg   = doc.metadata.get("page", "—")
                                src  = os.path.basename(doc.metadata.get("source", "unknown"))
                                score = doc.metadata.get("score")
                                score_tag = f'<span style="color:#ffd32a;margin-left:10px;font-size:0.75rem;">RELEVANCE: {score:.2f}</span>' if score else ""
                                
                                st.markdown(f"""
                                <div class="chunk-box">
                                    <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                                        <span style="color:#00d4ff; font-weight:bold; font-size:0.8rem;">CHUNK {i+1}</span>
                                        <span style="color:#4a5a7a; font-size:0.75rem;">{src} (p. {pg}){score_tag}</span>
                                    </div>
                                    <div style="color:#8090aa; line-height:1.5; font-size:0.85rem;">{doc.page_content[:450]}…</div>
                                </div>
                                """, unsafe_allow_html=True)

                    # RAG Evaluation Metrics (New Response)
                    m = resp.get("metrics")
                    if m:
                        c_sc = int(m.get("avg_context_score", 0) * 100)
                        a_sc = int(m.get("answer_relevancy", 0) * 100)
                        r_lt = m.get("retrieval_latency", 0)
                        g_lt = m.get("generation_latency", 0)
                        
                        st.markdown(f"""
                        <div style="display:flex; gap:15px; margin-top:5px; padding:8px 12px; 
                                    background:rgba(255,255,255,0.03); border-radius:6px; border:1px solid rgba(255,255,255,0.08);">
                            <div style="font-size:0.7rem; color:#4a5a7a;">
                                <span style="color:#8090aa; font-weight:600;">CONTEXT MATCH:</span> 
                                <span style="color:#00d4ff; font-family:'JetBrains Mono',monospace;">{c_sc}%</span>
                            </div>
                            <div style="font-size:0.7rem; color:#4a5a7a; border-left:1px solid rgba(255,255,255,0.1); padding-left:15px;">
                                <span style="color:#8090aa; font-weight:600;">ANSWER RELEVANCY:</span> 
                                <span style="color:#ffd32a; font-family:'JetBrains Mono',monospace;">{a_sc}%</span>
                            </div>
                            <div style="font-size:0.7rem; color:#4a5a7a; border-left:1px solid rgba(255,255,255,0.1); padding-left:15px;">
                                <span style="color:#8090aa; font-weight:600;">LATENCY (R/G):</span> 
                                <span style="color:#00ff88; font-family:'JetBrains Mono',monospace;">{r_lt}s / {g_lt}s</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Record in History
                    st.session_state.query_history.insert(0, {
                        "query": prompt,
                        "answer": answer,
                        "sources": sources,
                        "iocs": iocs,
                        "metrics": m,
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                    })
                    # Keep only last 15
                    if len(st.session_state.query_history) > 15:
                        st.session_state.query_history.pop()

                    # Persist
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "confidence": sc,
                        "sources": sources,
                        "iocs": iocs,
                        "timeline": resp.get("timeline", []),
                        "metrics": m
                    })
                except Exception as ex:
                    st.error(f"Query error: {str(ex)}")
        else:
            warn = ("⚠️ No documents loaded. Upload and process reports "
                    "via the **Threat Intel Control Panel** in the sidebar first.")
            st.markdown(f"""
            <div class="bbl-ai-tag">🛡️ CTI ANALYST AI</div>
            <div class="bbl-ai">{warn}</div>
            """, unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": warn})
