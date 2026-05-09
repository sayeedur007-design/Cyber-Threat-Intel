"""
CTI RAG Engine — Robust version
"""
import os
import re
import tempfile
import logging
import time
import json
from dotenv import load_dotenv

# LangChain Imports
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever

try:
    from langchain.retrievers import EnsembleRetriever
except ImportError:
    try:
        from langchain_community.retrievers import EnsembleRetriever
    except ImportError:
        from langchain_classic.retrievers import EnsembleRetriever

# Optional PDF fallbacks
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
try:
    import pypdf
except ImportError:
    pypdf = None

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("cti_rag")

# ── Config ──────────────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHUNK_SIZE      = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP   = 150
TOP_K           = int(os.getenv("TOP_K", "5"))

CTI_PROMPT = ChatPromptTemplate.from_template("""\
You are a senior Cyber Threat Intelligence (CTI) analyst and Detection Engineer assistant inside a professional CTI platform.
Your task is to answer user threat-intelligence and detection-engineering questions using retrieved RAG context with high analytical quality.

STRICT ANALYTICAL RULES:
1. Write like a real human CTI analyst/defender, not a robotic AI.
2. Use clear sections with headings and bullet points.
3. Use relevant emojis naturally: 🛡️, 🌐, 📡, 🎯, 📊, 🔍, ⚠️, 🛠️, 📉.
4. Explain WHY detection or attribution matters operationally.
5. Mention exact infrastructure overlaps, TTP overlaps, and malware similarities.
6. Responses must feel like professional intelligence or detection briefings.

DETECTION & BLUE TEAM SPECIALIZATION:
If the question involves kill chains, ATT&CK, SIEM, telemetry, or detection gaps:
1. Map ATT&CK techniques to: Attacker Action, Process Behavior, Windows Logs (Event IDs), Sysmon Logs, EDR Telemetry, and Network Indicators.
2. Explicitly identify: Strongest detection stage, weakest detection stage, and likely SOC blind spots.
3. Explain detection difficulty: Encrypted traffic, LOLBins, Direct Syscalls, Memory-only malware, Process Injection, etc.
4. Use structured Markdown tables for ATT&CK mappings, Event IDs, and Detection Coverage.
5. Prioritize operational security reasoning and "Blue Team" usefulness over generic summaries.

RESPONSE FORMAT:
# 🎯 Executive Assessment
Concise 2–4 sentence strategic summary.

# 🌐 Infrastructure & Correlation
Detailed analysis of shared domains, IPs, DNS overlaps, and hosting.

# 🛠️ Detection Engineering & Telemetry
If applicable, provide tables mapping techniques to Event IDs and telemetry sources.
Explain detection gaps and blind spots.

# 🛡️ Threat Actor / Campaign Overlap
List known actors or campaigns sharing malware family, TTPs, or victimology.

# 🔍 Evidence & Indicators
Specific indicators (IPs, Hashes, Domains, CVEs) found in context.

# ⚠️ Analytical Caveats & Blind Spots
Mention uncertainty, infrastructure reuse, or specific detection hurdles (LOLBins, etc.).

# 📊 Attribution & Detection Confidence
* Confidence Level (Low / Medium / High)
* Justification (e.g., "High based on unique TTP overlap with APT41")

IMPORTANT:
* Do NOT hallucinate. Only use retrieved context.
* If evidence is weak or indirect, label it clearly.
* Keep responses concise but intelligence-dense.
* Use clean markdown tables for technical data.

Context:
{context}

Question: {question}

Answer:""")


# ── PDF loading with fallbacks ───────────────────────────────────
def _load_pdf(path: str) -> list:
    docs = []
    # Method 1: PyPDFLoader
    try:
        loader = PyPDFLoader(path)
        docs = loader.load()
        if sum(len(d.page_content.strip()) for d in docs) > 100:
            return docs
    except Exception as e:
        log.warning(f"PyPDFLoader failed: {e}")

    # Method 2: pdfplumber
    if pdfplumber:
        try:
            with pdfplumber.open(path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        docs.append(Document(page_content=text, metadata={"source": path, "page": i + 1}))
            if sum(len(d.page_content.strip()) for d in docs) > 100:
                return docs
        except Exception as e:
            log.warning(f"pdfplumber failed: {e}")

    # Method 3: pypdf direct
    if pypdf:
        try:
            reader = pypdf.PdfReader(path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if text.strip():
                    docs.append(Document(page_content=text, metadata={"source": path, "page": i + 1}))
            return docs
        except Exception as e:
            log.warning(f"pypdf direct failed: {e}")

    return []


def _format_docs(docs: list) -> str:
    parts = []
    for i, d in enumerate(docs, 1):
        src  = d.metadata.get("source", "doc")
        page = d.metadata.get("page", "?")
        parts.append(f"[Chunk {i} | {os.path.basename(src)} p.{page}]\n{d.page_content}")
    return "\n\n---\n\n".join(parts)


# ── Regex Patterns ─────────────────────────────────────────────
_RE_URL    = re.compile(r'https?://[^\s\)\]\'\"<>]+')
_RE_IP     = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
_RE_DOMAIN = re.compile(r'\b(?:[a-zA-Z0-9\-]+\[?\.\]?)+(?:com|net|org|io|gov|edu|ru|cn|uk|onion|biz|top)\b')
_RE_HASH   = re.compile(r'\b[a-fA-F0-9]{32}\b|\b[a-fA-F0-9]{40}\b|\b[a-fA-F0-9]{64}\b')
_RE_CVE    = re.compile(r'\bCVE-\d{4}-\d{4,7}\b', re.IGNORECASE)
_RE_EMAIL  = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

def extract_indicators(text: str) -> dict:
    return {
        "ips":     list(set(_RE_IP.findall(text))),
        "domains": list(set(_RE_DOMAIN.findall(text))),
        "hashes":  list(set(_RE_HASH.findall(text))),
        "cves":    list(set(_RE_CVE.findall(text))),
        "urls":    list(set(_RE_URL.findall(text))),
        "emails":  list(set(_RE_EMAIL.findall(text)))
    }

# ── Main Engine ─────────────────────────────────────────────────
class CTI_RAG_Engine:
    def __init__(self):
        log.info("Initialising RAG Engine...")
        self.embeddings = None
        self.llm = None
        self.vector_store = None
        self.ensemble_retriever = None
        self.chunk_count = 0

        try:
            log.info(f"Loading embeddings model: {EMBEDDING_MODEL}")
            self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        except Exception as e:
            log.error(f"Failed to load embeddings: {e}")

        try:
            log.info(f"Connecting to Ollama at {OLLAMA_BASE_URL} (Model: {OLLAMA_MODEL})")
            self.llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.1)
        except Exception as e:
            log.error(f"Failed to connect to Ollama: {e}")

    def process_files(self, uploaded_files) -> tuple:
        all_docs = []
        try:
            with tempfile.TemporaryDirectory() as tmp:
                for uf in uploaded_files:
                    path = os.path.join(tmp, uf.name)
                    with open(path, "wb") as f:
                        f.write(uf.getbuffer())
                    
                    if uf.name.lower().endswith(".pdf"):
                        docs = _load_pdf(path)
                    else:
                        try:
                            docs = TextLoader(path, encoding="utf-8").load()
                        except:
                            docs = TextLoader(path, encoding="latin-1").load()
                    all_docs.extend(docs)

            if not all_docs:
                return False, "No readable text found."

            if not self.embeddings:
                return False, "Embeddings model not loaded. Check backend logs."

            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            faiss_ret = self.vector_store.as_retriever(search_kwargs={"k": TOP_K})
            bm25_ret = BM25Retriever.from_documents(chunks)
            bm25_ret.k = TOP_K
            
            self.ensemble_retriever = EnsembleRetriever(retrievers=[faiss_ret, bm25_ret], weights=[0.6, 0.4])
            self.chunk_count = len(chunks)
            return True, f"✅ Indexed {len(chunks)} chunks."
        except Exception as e:
            return False, f"Processing error: {e}"

    def query(self, question: str) -> dict:
        if not self.ensemble_retriever:
            return {"answer": "No docs loaded.", "context": [], "iocs": {}, "metrics": {}}

        start_time = time.time()
        try:
            # 1. Retrieval
            r_start = time.time()
            context_docs = self.ensemble_retriever.invoke(question)
            r_end = time.time()
            ctx_text = _format_docs(context_docs)

            # 2. Generation
            if not self.llm:
                return {"answer": "⚠️ AI service (Ollama) is not initialized. Please check connection.", "context": context_docs, "iocs": extract_indicators(ctx_text), "metrics": {}}

            g_start = time.time()
            try:
                chain = ({"context": RunnableLambda(lambda _: ctx_text), "question": RunnablePassthrough()} 
                         | CTI_PROMPT | self.llm | StrOutputParser())
                answer = chain.invoke(question)
            except Exception as e:
                log.error(f"Ollama generation error: {e}")
                return {"answer": f"⚠️ AI service error: {str(e)}. Please ensure Ollama is running.", "context": context_docs, "iocs": extract_indicators(ctx_text), "metrics": {}}
            g_end = time.time()
            
            # 3. Metrics (Optimized: Re-use query embedding)
            if not self.embeddings:
                 return {
                    "answer": answer, "context": context_docs, "iocs": extract_indicators(f"{ctx_text}\n{answer}"),
                    "timeline": [], "metrics": {"total_latency": round(time.time() - start_time, 3)}
                }

            try:
                q_vec = self.embeddings.embed_query(question)
                a_vec = self.embeddings.embed_query(answer)
                answer_relevancy = sum(a*b for a,b in zip(q_vec, a_vec))
                
                chunk_sims = [sum(q_vec[i]*c_vec[i] for i in range(len(q_vec))) 
                              for c_vec in [self.embeddings.embed_query(d.page_content) for d in context_docs]]
                avg_ctx_score = sum(chunk_sims) / len(chunk_sims) if chunk_sims else 0
            except Exception as e:
                log.warning(f"Metrics calculation failed: {e}")
                answer_relevancy, avg_ctx_score = 0, 0

            return {
                "answer": answer, "context": context_docs, "iocs": extract_indicators(f"{ctx_text}\n{answer}"),
                "timeline": [],
                "metrics": {
                    "retrieval_latency": round(r_end - r_start, 3), "generation_latency": round(g_end - g_start, 3),
                    "total_latency": round(time.time() - start_time, 3), "answer_relevancy": round(answer_relevancy, 3),
                    "avg_context_score": round(avg_ctx_score, 3)
                }
            }
        except Exception as e:
            log.error(f"General RAG query error: {e}")
            return {"answer": f"Internal Error: {str(e)}", "context": [], "iocs": {}, "metrics": {}}

    def extract_timeline(self, context: str) -> list:
        if not self.llm:
            return []
        prompt = ChatPromptTemplate.from_template("Extract a JSON timeline sequence: [{{'date': '...', 'event': '...'}}] from:\n{context}")
        try:
            res = (prompt | self.llm | StrOutputParser()).invoke({"context": context})
            match = re.search(r'(\[.*\])', res, re.DOTALL)
            return json.loads(match.group(0)) if match else []
        except Exception as e:
            log.warning(f"Timeline extraction failed: {e}")
            return []
