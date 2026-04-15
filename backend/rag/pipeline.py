from backend.rag.retriever import hybrid_search
from backend.rag.reranker import rerank
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(query):
    docs = hybrid_search(query)
    docs = rerank(query, docs)

    context = "\n".join(docs)

    prompt = f"""
    Answer strictly from context.

    Context:
    {context}

    Question:
    {query}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
