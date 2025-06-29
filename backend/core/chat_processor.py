import os
from typing import Optional, Tuple, List
from pathlib import Path
from fastapi import HTTPException
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq

from .models import DEFAULT_SYSTEM_PROMPT
from .chat_manager import ChatHistoryManager


def get_conversational_chain(model_name: str, system_prompt: Optional[str] = None):
    """Create conversational chain with custom system prompt"""
    if system_prompt is None:
        system_prompt = DEFAULT_SYSTEM_PROMPT
    
    # Ensure the system prompt includes all necessary placeholders
    if "{context}" not in system_prompt:
        system_prompt += "\n\nDocument Context:\n{context}"
    if "{chat_context}" not in system_prompt:
        system_prompt += "\n\nChat History Context:\n{chat_context}"
    if "{input}" not in system_prompt:
        system_prompt += "\n\nQuestion: {input}"
    
    groq_api_key = os.getenv('GROQ_API_KEY')
    llm = ChatGroq(groq_api_key=groq_api_key, model_name=model_name)
    prompt = ChatPromptTemplate.from_template(system_prompt)
    chain = create_stuff_documents_chain(llm, prompt)
    return chain


def process_question(
    question: str, 
    model_name: str, 
    session_id: str, 
    system_prompt: Optional[str] = None, 
    use_chat_history: bool = True
) -> Tuple[str, List[str], List[str]]:
    """Process user question and return answer with context preservation"""
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        session_dir = Path(f"sessions/{session_id}")
        
        if not (session_dir / "faiss_index").exists():
            raise HTTPException(status_code=400, detail="No processed documents found for this session")
        
        # Load document vector store
        vector_store = FAISS.load_local(
            str(session_dir / "faiss_index"), 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        
        retriever = vector_store.as_retriever()
        
        # Get chat history context if enabled
        chat_context = ""
        chat_context_sources = []
        if use_chat_history:
            chat_manager = ChatHistoryManager(session_id)
            chat_context, chat_context_sources = chat_manager.get_relevant_context(question)
        
        # Create custom chain that includes chat context
        chain = get_conversational_chain(model_name, system_prompt)
        
        # Create a custom retrieval chain that includes chat context
        def enhanced_chain(inputs):
            # Get document context
            docs = retriever.get_relevant_documents(inputs['input'])
            
            # Prepare inputs for the chain
            chain_inputs = {
                'input': inputs['input'],
                'context': docs,
                'chat_context': chat_context
            }
            
            # Get response from chain
            response = chain.invoke(chain_inputs)
            
            return {
                'answer': response,
                'context': docs,
                'chat_context': chat_context
            }
        
        response = enhanced_chain({'input': question})
        
        # Format the answer with file and page references
        answer = response['answer']
        context_docs = response['context']
        
        # Add source information
        sources = set()
        for doc in context_docs:
            if 'file' in doc.metadata and 'page' in doc.metadata:
                sources.add(f"{doc.metadata['file']} (page {doc.metadata['page']})")
        
        # Add chat history to vector store for future context
        if use_chat_history:
            chat_manager = ChatHistoryManager(session_id)
            chat_manager.add_to_history(question, answer, list(sources))
        
        return answer, list(sources), chat_context_sources
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")