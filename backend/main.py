import os
import uuid
import tempfile
from typing import List
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
from dotenv import load_dotenv

# Import core modules
from core import (
    ChatMessage,
    ChatResponse,
    ProcessResponse,
    SystemPromptUpdate,
    MODEL_OPTIONS,
    DEFAULT_SYSTEM_PROMPT,
    process_pdf_files,
    ChatHistoryManager,
    process_question,
    generate_pdf_report,
    session_manager
)

# Load environment variables
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# FastAPI app
app = FastAPI(title="ChatPDF API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Routes
@app.get("/")
async def root():
    return {"message": "ChatPDF API with Context Preservation is running"}


@app.get("/models")
async def get_models():
    """Get available LLM models"""
    return {"models": MODEL_OPTIONS}


@app.post("/upload", response_model=ProcessResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and process PDF files"""
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Validate file types
    for file in files:
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
    
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Process PDFs using core module
        process_pdf_files(files, session_id)
        
        # Initialize session using session manager
        file_names = [file.filename for file in files]
        session_manager.create_session(session_id, file_names)
        
        return ProcessResponse(
            message="Documents processed successfully",
            session_id=session_id,
            processed=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")


@app.post("/chat/{session_id}", response_model=ChatResponse)
async def chat(session_id: str, message: ChatMessage):
    """Send a message and get response with context preservation"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not session_manager.is_session_processed(session_id):
        raise HTTPException(status_code=400, detail="No processed documents found")
    
    try:
        # Get system prompt from session if not provided
        system_prompt = message.system_prompt or session_manager.get_system_prompt(session_id)
        
        answer, sources, chat_context_sources = process_question(
            message.question, 
            message.model_name, 
            session_id, 
            system_prompt,
            message.use_chat_history
        )
        
        # Update session history using session manager
        session_manager.add_to_history(session_id, "user", message.question)
        session_manager.add_to_history(session_id, "assistant", answer)
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            session_id=session_id,
            chat_context_used=chat_context_sources
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.put("/system-prompt/{session_id}")
async def update_system_prompt(session_id: str, prompt_data: SystemPromptUpdate):
    """Update the system prompt for a session"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_manager.set_system_prompt(session_id, prompt_data.system_prompt)
    return {"message": "System prompt updated successfully"}


@app.get("/system-prompt/{session_id}")
async def get_system_prompt(session_id: str):
    """Get the current system prompt for a session"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    current_prompt = session_manager.get_system_prompt(session_id)
    return {
        "system_prompt": current_prompt if current_prompt else DEFAULT_SYSTEM_PROMPT,
        "is_default": current_prompt is None
    }


@app.delete("/system-prompt/{session_id}")
async def reset_system_prompt(session_id: str):
    """Reset system prompt to default for a session"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    session_manager.reset_system_prompt(session_id)
    return {"message": "System prompt reset to default"}


@app.get("/history/{session_id}")
async def get_history(session_id: str):
    """Get chat history for a session"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = session_manager.get_history(session_id)
    return {"history": history}


@app.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear chat history for a session"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clear in-memory history using session manager
    session_manager.clear_history(session_id)
    
    # Clear chat history vector store
    chat_manager = ChatHistoryManager(session_id)
    chat_manager.clear_history()
    
    return {"message": "Chat history cleared"}


@app.get("/download/{session_id}")
async def download_history(session_id: str):
    """Download chat history as PDF"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    history = session_manager.get_history(session_id)
    if not history:
        raise HTTPException(status_code=400, detail="No chat history to download")
    
    try:
        pdf = generate_pdf_report(history)
        
        # Save PDF to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf.output(tmp_file.name)
            
            return FileResponse(
                tmp_file.name,
                media_type='application/pdf',
                filename=f"chat_history_{session_id}.pdf"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")


@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_manager.get_session_info(session_id)


@app.get("/chat-context/{session_id}")
async def get_chat_context_preview(session_id: str, question: str):
    """Preview what chat context would be retrieved for a question"""
    if not session_manager.session_exists(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    chat_manager = ChatHistoryManager(session_id)
    chat_context, context_sources = chat_manager.get_relevant_context(question)
    
    return {
        "chat_context": chat_context,
        "context_sources": context_sources,
        "has_context": bool(chat_context)
    }


# Cleanup background task
@app.on_event("startup")
async def startup_event():
    """Initialize the application"""
    # Create sessions directory
    Path("sessions").mkdir(exist_ok=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    session_manager.cleanup_old_sessions()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)