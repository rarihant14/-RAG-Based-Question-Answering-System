from langchain.tools import Tool
from backend.rag.pipeline import generate_answer

def rag_tool_func(query):
    return generate_answer(query)

rag_tool = Tool(
    name="RAG_QA",
    func=rag_tool_func,
    description="Answer questions using uploaded documents"
)
