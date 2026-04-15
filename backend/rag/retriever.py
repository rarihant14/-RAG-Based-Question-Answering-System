from backend.vectorstore.faiss_store import query_index
from rank_bm25 import BM25Okapi

def hybrid_search(query):
    texts = query_index(query, top_k=5)
    if not texts:
        return []

    bm25 = BM25Okapi([t.split() for t in texts])
    scores = bm25.get_scores(query.split())

    ranked = sorted(zip(texts, scores), key=lambda x: x[1], reverse=True)

    return [r[0] for r in ranked[:3]]
