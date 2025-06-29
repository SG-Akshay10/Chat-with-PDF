import os
import shutil
import datetime
from typing import List, Optional, Tuple
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class ChatHistoryManager:
    """Manages chat history vector store for context preservation"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.session_dir = Path(f"sessions/{session_id}")
        self.chat_history_path = self.session_dir / "chat_history_index"
        
    def add_to_history(self, user_question: str, assistant_answer: str, sources: List[str] = None):
        """Add a conversation pair to the chat history vector store"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create conversation context with metadata
        conversation_text = f"User Question: {user_question}\nAssistant Answer: {assistant_answer}"
        if sources:
            conversation_text += f"\nSources: {', '.join(sources)}"
        
        metadata = {
            "type": "conversation",
            "timestamp": timestamp,
            "user_question": user_question,
            "assistant_answer": assistant_answer,
            "sources": sources or []
        }
        
        try:
            # Try to load existing vector store
            if self.chat_history_path.exists():
                chat_history_store = FAISS.load_local(
                    str(self.chat_history_path), 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                # Add new conversation
                chat_history_store.add_texts([conversation_text], metadatas=[metadata])
            else:
                # Create new vector store
                chat_history_store = FAISS.from_texts(
                    [conversation_text], 
                    embedding=self.embeddings, 
                    metadatas=[metadata]
                )
            
            # Save updated vector store
            self.session_dir.mkdir(parents=True, exist_ok=True)
            chat_history_store.save_local(str(self.chat_history_path))
            
        except Exception as e:
            print(f"Error adding to chat history: {str(e)}")
    
    def get_relevant_context(self, current_question: str, max_results: int = 3) -> Tuple[str, List[str]]:
        """Retrieve relevant chat history context for the current question"""
        if not self.chat_history_path.exists():
            return "", []
        
        try:
            chat_history_store = FAISS.load_local(
                str(self.chat_history_path), 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            
            # Search for relevant previous conversations
            retriever = chat_history_store.as_retriever(search_kwargs={"k": max_results})
            relevant_docs = retriever.get_relevant_documents(current_question)
            
            if not relevant_docs:
                return "", []
            
            # Format the context
            chat_context_parts = []
            context_sources = []
            
            for doc in relevant_docs:
                metadata = doc.metadata
                context_parts = []
                
                if 'user_question' in metadata and 'assistant_answer' in metadata:
                    context_parts.append(f"Previous Q: {metadata['user_question']}")
                    context_parts.append(f"Previous A: {metadata['assistant_answer']}")
                    
                    if metadata.get('sources'):
                        context_parts.append(f"Sources: {', '.join(metadata['sources'])}")
                    
                    context_sources.append(f"Previous conversation from {metadata.get('timestamp', 'unknown time')}")
                
                if context_parts:
                    chat_context_parts.append('\n'.join(context_parts))
            
            chat_context = '\n\n---\n\n'.join(chat_context_parts) if chat_context_parts else ""
            return chat_context, context_sources
            
        except Exception as e:
            print(f"Error retrieving chat context: {str(e)}")
            return "", []
    
    def clear_history(self):
        """Clear the chat history vector store"""
        if self.chat_history_path.exists():
            shutil.rmtree(self.chat_history_path)