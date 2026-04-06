# rag_engine.py
import fitz  # PyMuPDF
import math

# ── In-memory vector store (no external DB needed) ──────────────────────────
_chunks: list[str] = []
_embeddings: list[list[float]] = []

# ── Step 1: Split policy PDF into chunks ─────────────────────────────────────
def _extract_chunks(pdf_path: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    words = full_text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        start += chunk_size - overlap  # overlap so we don't cut mid-sentence
    return chunks

# ── Step 2: Simple TF-IDF-style embedding (no API cost, no setup) ────────────
def _embed(text: str) -> list[float]:
    """
    Lightweight word-frequency vector.
    Good enough for policy retrieval without any API calls.
    """
    words = text.lower().split()
    freq: dict[str, int] = {}
    for w in words:
        # strip punctuation
        w = "".join(c for c in w if c.isalnum())
        if w:
            freq[w] = freq.get(w, 0) + 1

    total = sum(freq.values()) or 1
    return {w: count / total for w, count in freq.items()}

def _cosine(a: dict, b: dict) -> float:
    """Cosine similarity between two frequency dicts."""
    dot = sum(a.get(w, 0) * b.get(w, 0) for w in b)
    mag_a = math.sqrt(sum(v * v for v in a.values())) or 1
    mag_b = math.sqrt(sum(v * v for v in b.values())) or 1
    return dot / (mag_a * mag_b)

# ── Step 3: Index the policy (called once at startup) ────────────────────────
def index_policy(pdf_path: str) -> None:
    global _chunks, _embeddings
    try:
        _chunks = _extract_chunks(pdf_path)
        _embeddings = [_embed(c) for c in _chunks]
        print(f"[RAG] Indexed {len(_chunks)} chunks from {pdf_path}")
    except Exception as e:
        print(f"[RAG] Warning: could not index policy — {e}")
        _chunks, _embeddings = [], []

# ── Step 4: Retrieve top-k most relevant chunks ───────────────────────────────
def retrieve_relevant_policy(query: str, top_k: int = 3) -> str:
    if not _chunks:
        return "(policy not indexed)"

    query_vec = _embed(query)
    scores = [(_cosine(query_vec, emb), i) for i, emb in enumerate(_embeddings)]
    scores.sort(reverse=True)

    top_chunks = [_chunks[i] for _, i in scores[:top_k]]
    return "\n\n---\n\n".join(top_chunks)