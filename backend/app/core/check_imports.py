import sys
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("diagnostic")

def check_package(package_name):
    try:
        __import__(package_name.replace("-", "_"))
        log.info(f"[OK] {package_name} is installed.")
        return True
    except ImportError:
        log.error(f"[MISSING] {package_name} is MISSING.")
        return False

def run_diagnostics():
    print("=" * 50)
    print("  CTI ANALYST PLATFORM — DIAGNOSTIC TOOL")
    print("=" * 50)
    
    required = [
        "langchain",
        "langchain-community",
        "langchain-ollama",
        "langchain-huggingface",
        "langchain-core",
        "langchain-text-splitters",
        "streamlit",
        "faiss",
        "sentence-transformers",
        "pypdf",
        "pdfplumber",
        "pandas",
        "plotly",
        "reportlab"
    ]
    
    passed = 0
    for pkg in required:
        if check_package(pkg):
            passed += 1
            
    print("-" * 50)
    print(f"Results: {passed}/{len(required)} packages found.")
    
    if passed < len(required):
        print("\nACTION REQUIRED: Run 'pip install -r requirements.txt'")
    else:
        print("\nSUCCESS: All dependencies are satisfied.")
    print("=" * 50)

if __name__ == "__main__":
    run_diagnostics()
