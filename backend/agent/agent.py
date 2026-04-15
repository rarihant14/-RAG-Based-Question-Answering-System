from langchain.agents import initialize_agent, AgentType
from langchain_groq import ChatGroq
from backend.agent.tools import rag_tool
from backend.agent.memory import memory
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    streaming=True
)

agent = initialize_agent(
    tools=[rag_tool],
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True
)
