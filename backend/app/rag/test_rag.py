"""
Quick end-to-end test for CTI RAG Engine using new query() API.
"""
import os
import sys

class MockFile:
    """Mimics Streamlit UploadedFile for testing."""
    def __init__(self, name: str, path: str):
        self.name = name
        self._path = path
    def getbuffer(self):
        with open(self._path, "rb") as f:
            return f.read()


def test_rag():
    print("=" * 55)
    print("  CTI RAG ENGINE — End-to-End Test")
    print("=" * 55)

    from app.rag.rag_engine import CTI_RAG_Engine

    engine = CTI_RAG_Engine()

    # Process sample file
    sample = "sample_cti.txt"
    if not os.path.exists(sample):
        print(f"ERROR: {sample} not found")
        sys.exit(1)

    mock = MockFile(sample, sample)
    ok, msg = engine.process_files([mock])
    # Handle Windows terminal encoding for emojis
    msg_to_print = msg.encode('ascii', 'replace').decode('ascii')
    print(f"\n[INGEST] {msg_to_print}")
    if not ok:
        print("FAILED: ingest step")
        sys.exit(1)

    # Test questions
    tests = [
        ("What is the C2 domain?",   ["evil-server"]),
        ("Who is the threat actor?", ["APT29", "Cozy Bear"]),
        ("What malware was used?",   ["QuickSteal"]),
        ("What is the file hash?",   ["e3b0c"]),
    ]

    passed = 0
    for q, expected_terms in tests:
        print(f"\n[Q] {q}")
        result  = engine.query(q)
        answer  = result["answer"]
        n_chunks = len(result["context"])
        print(f"[A] {answer[:200]}")
        print(f"    Retrieved {n_chunks} chunk(s)")

        hit = any(t.lower() in answer.lower() for t in expected_terms)
        # Handle Windows terminal encoding for emojis
        status_raw = "✅ PASS" if hit else "❌ FAIL"
        status = status_raw.encode('ascii', 'replace').decode('ascii')
        print(f"    {status} (looking for: {expected_terms})")
        if hit:
            passed += 1

    print(f"\n{'='*55}")
    print(f"  Results: {passed}/{len(tests)} passed")
    print(f"{'='*55}")


if __name__ == "__main__":
    test_rag()
