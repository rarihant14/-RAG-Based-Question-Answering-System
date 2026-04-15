import time
import uuid

from pinecone import Pinecone, ServerlessSpec

from backend.config import (
    EMBEDDING_DIMENSION,
    PINECONE_API_KEY,
    PINECONE_CLOUD,
    PINECONE_INDEX_NAME,
    PINECONE_REGION,
)
from backend.rag.embeddings import embed


def _list_index_names(client):
    indexes = client.list_indexes()

    if hasattr(indexes, "names"):
        return set(indexes.names())

    names = set()
    for index_info in indexes:
        if isinstance(index_info, str):
            names.add(index_info)
        elif isinstance(index_info, dict):
            names.add(index_info.get("name"))
        else:
            names.add(getattr(index_info, "name", None))

    return {name for name in names if name}


def _index_ready(client):
    status = client.describe_index(PINECONE_INDEX_NAME).status
    if isinstance(status, dict):
        return status.get("ready", False)
    return getattr(status, "ready", False)


def get_index():
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is not configured.")

    client = Pinecone(api_key=PINECONE_API_KEY)
    existing_indexes = _list_index_names(client)

    if PINECONE_INDEX_NAME not in existing_indexes:
        client.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
        )

    while not _index_ready(client):
        time.sleep(1)

    return client.Index(PINECONE_INDEX_NAME)


def save_index(texts):
    index = get_index()
    embeddings = embed(texts).tolist()
    vectors = []

    for text, embedding in zip(texts, embeddings):
        vectors.append(
            {
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": {"text": text},
            }
        )

    if vectors:
        index.upsert(vectors=vectors)


def query_index(query, top_k=5):
    index = get_index()
    query_embedding = embed([query])[0].tolist()
    response = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    matches = response.get("matches", []) if isinstance(response, dict) else getattr(response, "matches", [])

    return [
        (match.get("metadata", {}) if isinstance(match, dict) else getattr(match, "metadata", {})).get("text", "")
        for match in matches
        if (match.get("metadata", {}) if isinstance(match, dict) else getattr(match, "metadata", {})).get("text")
    ]
