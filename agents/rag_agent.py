"""
RAGAgent: Agente de búsqueda y generación con Chroma Vector Database
"""
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

from mistralai import Mistral

from IndustrialRAG.config.settings import config
from IndustrialRAG.utils.text_processor import process_pdf_to_chunks, clean_text


logger = logging.getLogger(__name__)


class RAGAgent:
    """
    Agente RAG que usa Chroma para búsqueda vectorial en documentos técnicos
    """
    
    def __init__(self, chroma_client: chromadb.Client, collection_name: str = None):
        """
        Inicializa el RAGAgent
        
        Args:
            chroma_client: Cliente de Chroma
            collection_name: Nombre de la colección (opcional)
        """
        self.chroma_client = chroma_client
        self.collection_name = collection_name or config.chroma.collection_name
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=config.chroma.embedding_model
        )
        
        # Inicializar cliente Mistral
        self.mistral_client = Mistral(api_key=config.mistral.api_key)
        
        # Obtener o crear la colección
        self.collection = self._get_or_create_collection()
    
    def _get_or_create_collection(self) -> chromadb.Collection:
        """Obtiene o crea una colección en Chroma"""
        try:
            return self.chroma_client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
        except Exception as e:
            logger.error(f"Error al obtener/crear colección {self.collection_name}: {str(e)}")
            raise
    
    def load_pdfs(self, pdf_dir: str) -> int:
        """
        Carga documentos PDF en la colección de Chroma
        
        Args:
            pdf_dir: Directorio con archivos PDF
            
        Returns:
            Número de chunks procesados
        """
        pdf_dir_path = Path(pdf_dir)
        if not pdf_dir_path.exists():
            raise FileNotFoundError(f"Directorio {pdf_dir} no existe")
        
        pdf_files = list(pdf_dir_path.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No se encontraron archivos PDF en {pdf_dir}")
            return 0
        
        total_chunks = 0
        for pdf_file in pdf_files:
            try:
                chunks = process_pdf_to_chunks(
                    pdf_file, 
                    chunk_size=config.chroma.chunk_size,
                    overlap=config.chroma.chunk_overlap
                )
                
                if not chunks:
                    logger.warning(f"No se extrajo texto de {pdf_file}")
                    continue
                
                # Añadir chunks a la colección
                ids = []
                documents = []
                metadatas = []
                
                for i, chunk in enumerate(chunks):
                    doc_id = f"{pdf_file.stem}_{i}"
                    ids.append(doc_id)
                    documents.append(chunk)
                    metadatas.append({
                        "source": str(pdf_file),
                        "chunk_id": i,
                        "file_name": pdf_file.name
                    })
                
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
                
                total_chunks += len(chunks)
                logger.info(f"Procesado {pdf_file.name}: {len(chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Error procesando {pdf_file}: {str(e)}")
                continue
        
        return total_chunks
    
    def search(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """
        Busca documentos relevantes para una consulta
        
        Args:
            query: Consulta de búsqueda
            top_k: Número máximo de resultados
            
        Returns:
            Diccionario con contextos, metadatos y distancias
        """
        try:
            results = self.collection.query(
                query_texts=[clean_text(query)],
                n_results=top_k
            )
            
            return {
                "contexts": results["documents"][0],
                "metadatas": results["metadatas"][0],
                "distances": results["distances"][0],
                "ids": results["ids"][0]
            }
        except Exception as e:
            logger.error(f"Error en búsqueda RAG: {str(e)}")
            return {
                "contexts": [],
                "metadatas": [],
                "distances": [],
                "ids": []
            }
    
    def generate_response(self, query: str, context: str = None) -> str:
        """
        Genera una respuesta basada en contexto
        
        Args:
            query: Consulta del usuario
            context: Contexto adicional (opcional)
            
        Returns:
            Respuesta generada por el modelo
        """
        if context and context.strip():
            prompt = f"""Eres un asistente técnico experto en mantenimiento industrial.
            Basado en el siguiente contexto técnico, responde la consulta de manera precisa y detallada.
            
            Contexto: {context}
            
            Consulta: {query}
            
            Requisitos:
            - Responde en español
            - Sé específico y técnico
            - Si no encuentras la respuesta en el contexto, indica que no tienes información suficiente
            - Incluye referencias a normativas o estándares cuando sea relevante"""
        else:
            prompt = f"""Eres un asistente técnico experto en mantenimiento industrial.
            Responde la siguiente consulta basado en tu conocimiento técnico.
            
            Consulta: {query}
            
            Requisitos:
            - Responde en español
            - Sé específico y técnico
            - Si no tienes información suficiente, indica que no puedes responder
            - Incluye referencias a normativas o estándares cuando sea relevante"""
        
        try:
            response = self.mistral_client.chat(
                model=config.mistral.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.mistral.temperature,
                max_tokens=config.mistral.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generando respuesta: {str(e)}")
            return f"Error al generar respuesta: {str(e)}"
    
    def query_with_context(self, query: str, top_k: int = 3) -> str:
        """
        Realiza una búsqueda y genera respuesta con el contexto encontrado
        
        Args:
            query: Consulta del usuario
            top_k: Número de resultados a considerar
            
        Returns:
            Respuesta generada con contexto
        """
        search_results = self.search(query, top_k)
        
        if not search_results["contexts"]:
            return self.generate_response(query, "No se encontró contexto relevante")
        
        # Combina todos los contextos
        combined_context = "\n\n---\n\n".join(search_results["contexts"])
        
        return self.generate_response(query, combined_context)
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Obtiene información sobre la colección"""
        try:
            return {
                "name": self.collection.name,
                "count": self.collection.count()
            }
        except Exception as e:
            logger.error(f"Error obteniendo info de colección: {str(e)}")
            return {"name": self.collection_name, "count": 0}
