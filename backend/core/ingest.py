import os
import tempfile
from typing import List
from pathlib import Path
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings


def get_pdf_text(pdf_files):
    """Extract text from PDF files"""
    text = ""
    file_page_mapping = []
    
    for pdf_file in pdf_files:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.file.read())
            tmp_file.flush()
            
            pdf_reader = PdfReader(tmp_file.name)
            file_name = pdf_file.filename
            
            for page_num, page in enumerate(pdf_reader.pages, start=1):
                page_text = page.extract_text()
                text += page_text
                file_page_mapping.append({
                    "text": page_text,
                    "file": file_name,
                    "page": page_num
                })
        
        # Clean up temporary file
        os.unlink(tmp_file.name)
    
    return text, file_page_mapping


def get_text_chunks(file_page_mapping):
    """Split text into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = []
    
    for item in file_page_mapping:
        chunk_items = text_splitter.split_text(item["text"])
        for chunk in chunk_items:
            chunks.append({
                "text": chunk,
                "file": item["file"],
                "page": item["page"]
            })
    return chunks


def get_vector_store(text_chunks, session_id):
    """Create and save vector store"""
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    texts = [chunk["text"] for chunk in text_chunks]
    metadatas = [{"file": chunk["file"], "page": chunk["page"]} for chunk in text_chunks]
    
    vector_store = FAISS.from_texts(texts, embedding=embeddings, metadatas=metadatas)
    
    # Create session directory
    session_dir = Path(f"sessions/{session_id}")
    session_dir.mkdir(parents=True, exist_ok=True)
    
    vector_store.save_local(str(session_dir / "faiss_index"))
    return vector_store


def process_pdf_files(pdf_files, session_id):
    """Process PDF files and create vector store"""
    raw_text, file_page_mapping = get_pdf_text(pdf_files)
    text_chunks = get_text_chunks(file_page_mapping)
    vector_store = get_vector_store(text_chunks, session_id)
    return vector_store