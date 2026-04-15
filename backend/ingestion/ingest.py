from backend.ingestion.loader import load_docs
from backend.ingestion.chunking import get_chunks
from backend.vectorstore.faiss_store import save_index

def ingest_file(path):
    docs = load_docs(path)
    chunks = get_chunks(docs)

    texts = [c.page_content for c in chunks]

    save_index(texts)
