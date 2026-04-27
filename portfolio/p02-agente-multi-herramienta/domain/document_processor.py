"""
domain/document_processor.py
----------------------------
Motor de procesamiento de documentos y búsqueda contextual (RAG).
Implementa fragmentación inteligente para no saturar el contexto del LLM.
"""

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

def extraer_texto_pdf(pdf_stream) -> str:
    """
    Extrae el texto plano de un stream de PDF subido por Streamlit.
    """
    try:
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
        texto = "".join([p.get_text("text") for p in doc])
        doc.close()
        return texto
    except Exception as e:
        print(f"🚨 Error al extraer texto del PDF: {e}")
        return ""

def fragmentar_texto(texto: str) -> list[str]:
    """
    Divide el texto en fragmentos (chunks) usando solapamiento para mantener el contexto.
    Usa los parámetros definidos en settings.py.
    """
    if not texto:
        return []
        
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "]
    )
    return splitter.split_text(texto)

def buscar_contexto_relevante(query: str, chunks: list[str], max_chunks: int = 3) -> str:
    """
    Busca los fragmentos más relevantes para una pregunta.
    Implementa un filtrado básico por palabras clave antes de enviar al LLM.
    """
    if not chunks:
        return "No hay contenido disponible en el documento."

    # [Inferencia] Filtrado por relevancia simple (palabras clave en común)
    palabras_query = set(query.lower().split())
    
    # Puntuamos cada fragmento según cuántas palabras de la pregunta contiene
    fragmentos_puntuados = []
    for c in chunks:
        puntos = sum(1 for p in palabras_query if p in c.lower())
        fragmentos_puntuados.append((puntos, c))
    
    # Ordenamos por relevancia y tomamos los mejores
    fragmentos_puntuados.sort(key=lambda x: x[0], reverse=True)
    mejores_fragmentos = [f[1] for f in fragmentos_puntuados[:max_chunks]]
    
    return "\n\n---\n\n".join(mejores_fragmentos)