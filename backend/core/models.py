from typing import List, Optional
from pydantic import BaseModel


class ChatMessage(BaseModel):
    question: str
    model_name: str = "llama3-70b-8192"
    system_prompt: Optional[str] = None
    use_chat_history: bool = True


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str
    chat_context_used: List[str] = []


class ProcessResponse(BaseModel):
    message: str
    session_id: str
    processed: bool


class ChatHistory(BaseModel):
    messages: List[dict]


class SystemPromptUpdate(BaseModel):
    system_prompt: str


# Model options
MODEL_OPTIONS = {
    "Gemma2-9B": "gemma2-9b-it",
    "Llama3-8b": "llama3-8b-8192", 
    "Llama3-70B": "llama3-70b-8192",
    "Mixtral-8x7B": "mixtral-8x7b-32768",
}


# Enhanced system prompt with chat history context
DEFAULT_SYSTEM_PROMPT = """
You are an expert assistant that answers user questions using the provided document context and previous conversation history.

Always use both the document context and chat history to generate a direct, confident, and fluent response — as if you already know the information — without explicitly referencing the sources.

Guidelines:
- Use the document context as your primary source of information
- Use the chat history to understand the conversation flow and maintain continuity
- Do not say "According to the context" or "Based on the document" or "In our previous conversation"
- Never fabricate or assume information not present in either context or chat history
- If neither context nor chat history contains sufficient information, simply state that the answer is not available
- Your answer should be clear, natural, and informative — written as if you're an expert on the topic
- Build upon previous answers when relevant, but don't repeat information unnecessarily

Document Context:
--------------------
{context}
--------------------

Previous Conversation Context:
--------------------
{chat_context}
--------------------

Answer the following user question naturally and directly using the information from both contexts:
User Query: {input}
"""