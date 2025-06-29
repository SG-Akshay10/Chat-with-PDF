from typing import List
from fpdf import FPDF


def generate_pdf_report(chat_history: List[dict]) -> FPDF:
    """Generate PDF report from chat history"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Add title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Chat History Report', ln=True, align='C')
    pdf.ln(10)
    
    # Reset font for content
    pdf.set_font("Arial", size=12)
    
    for msg in chat_history:
        msg_type = msg['type'].capitalize()
        content = msg['content']
        
        # Handle encoding issues
        content = content.encode('latin1', 'replace').decode('latin1')
        
        # Add message type as bold
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, f"{msg_type}:", ln=True)
        
        # Add message content
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"{content}\n")
        pdf.ln(5)
    
    return pdf