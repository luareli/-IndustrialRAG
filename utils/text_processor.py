"""
Utilidades para procesamiento de texto y PDFs
"""
import re
from typing import List
from pathlib import Path
import pypdf


def clean_text(text: str) -> str:
    """Limpia texto eliminando caracteres no válidos y espacios múltiples"""
    if not text:
        return ""
    
    # Eliminar caracteres de control no imprimibles
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    
    # Reemplazar espacios múltiples con uno solo
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar espacios al inicio y final
    text = text.strip()
    
    return text


def extract_pdf_text(pdf_path: Path) -> str:
    """Extrae texto de un archivo PDF"""
    try:
        with open(pdf_path, "rb") as f:
            reader = pypdf.PdfReader(f)
            text = "\n".join([
                clean_text(page.extract_text()) 
                for page in reader.pages 
                if page.extract_text()
            ])
            return text
    except Exception as e:
        raise ValueError(f"Error al leer PDF {pdf_path}: {str(e)}")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Divide texto en chunks con superposición (sliding window)
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño máximo de cada chunk
        overlap: Número de caracteres de superposición entre chunks
        
    Returns:
        Lista de chunks
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        
        if chunk:  # Solo añadir chunks no vacíos
            chunks.append(chunk)
        
        # Avanzar con superposición
        start = end - overlap if end - overlap > start else end
    
    return chunks


def process_pdf_to_chunks(pdf_path: Path, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Procesa un PDF completo y lo divide en chunks"""
    text = extract_pdf_text(pdf_path)
    return chunk_text(text, chunk_size, overlap)
