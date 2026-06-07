"""
WorkflowOrchestrator: Orquestador que combina respuestas de RAG y Database agents
"""
import logging
import json
from typing import Dict, List, Any, Optional

# Compatibilidad con mistralai 1.x y 2.x
try:
    from mistralai import Mistral
except ImportError:
    try:
        from mistralai.client import MistralClient as Mistral
    except ImportError:
        raise ImportError("mistralai no está instalado o la versión no es compatible (requiere >=1.2.0,>=2.0.0)")

from config.settings import config
from agents.rag_agent import RAGAgent
from agents.database_agent import DatabaseQueryAgent


logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    """
    Orquestador que combina respuestas de múltiples agentes
    """
    
    def __init__(self, rag_agent: RAGAgent, db_agent: DatabaseQueryAgent):
        """
        Inicializa el WorkflowOrchestrator
        
        Args:
            rag_agent: Instancia de RAGAgent
            db_agent: Instancia de DatabaseQueryAgent
        """
        self.rag_agent = rag_agent
        self.db_agent = db_agent
        self.mistral_client = Mistral(api_key=config.mistral.api_key)
        
        # Detectar el método chat correcto (compatibilidad 1.x y 2.x)
        if hasattr(self.mistral_client.chat, 'complete'):
            self._chat_method = lambda model, messages, **kwargs: \
                self.mistral_client.chat.complete(model=model, messages=messages, **kwargs)
        elif hasattr(self.mistral_client.chat, 'completions'):
            self._chat_method = lambda model, messages, **kwargs: \
                self.mistral_client.chat.completions.create(model=model, messages=messages, **kwargs)
        else:
            self._chat_method = lambda model, messages, **kwargs: \
                self.mistral_client.chat(model=model, messages=messages, **kwargs)
    
    def _combine_results(self, rag_response: str, db_response: str, query: str) -> str:
        """
        Combina respuestas de RAG y Database en una respuesta unificada
        
        Args:
            rag_response: Respuesta del agente RAG
            db_response: Respuesta del agente de base de datos
            query: Consulta original
            
        Returns:
            Respuesta combinada y mejorada
        """
        prompt = f"""Eres un asistente técnico experto en mantenimiento industrial.
        Tu tarea es crear una respuesta unificada, coherente y detallada combinando la información de dos fuentes:
        
        1. Documentación técnica (RAG):
        {rag_response}
        
        2. Base de datos:
        {db_response}
        
        Consulta original del usuario: {query}
        
        Directrices para la respuesta final:
        - Integrar información de ambas fuentes de manera lógica
        - Priorizar información de seguridad y normativas
        - Si hay contradicciones, explicar las diferencias
        - Incluir detalles técnicos específicos (números de parte, fechas, estados)
        - Responder en español
        - Estructurar la respuesta con encabezos claros
        - Si no hay información relevante, indicar que no se encontró datos
        
        Formato sugerido:
        [Respuesta Directa]
        [Detalles Técnicos]
        [Referencias/Normativas]
        [Recomendaciones]"""
        
        try:
            response = self._chat_method(
                model=config.mistral.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=config.mistral.temperature,
                max_tokens=config.mistral.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error combinando resultados: {str(e)}")
            return f"Error al combinar resultados: {str(e)}"
    
    def _determine_query_type(self, query: str) -> str:
        """
        Determina el tipo de consulta para priorizar el agente adecuado
        
        Args:
            query: Consulta del usuario
            
        Returns:
            Tipo de consulta: 'documentation', 'database', o 'both'
        """
        query_lower = query.lower()
        
        # Palabras clave para documentación
        doc_keywords = [
            'procedimiento', 'manual', 'guía', 'especificación', 'normativa',
            'instrucciones', 'mantenimiento preventivo', 'protocolos', 'estándar',
            'cómo', 'qué es', 'definición', 'características', 'funcionamiento'
        ]
        
        # Palabras clave para base de datos
        db_keywords = [
            'equipo', 'máquina', 'id', 'número de serie', 'estado', 'fecha',
            'últimos', 'historial', 'registro', 'cuántos', 'liste', 'enumere',
            'filtro', 'búsqueda', 'consulta', 'datos', 'tabla'
        ]
        
        doc_score = sum(1 for kw in doc_keywords if kw in query_lower)
        db_score = sum(1 for kw in db_keywords if kw in query_lower)
        
        # Si hay empate o ambos tienen puntuación, usar ambos
        if doc_score > db_score:
            return 'documentation'
        elif db_score > doc_score:
            return 'database'
        else:
            return 'both'
    
    def handle_query(self, query: str, use_rag: bool = True, use_db: bool = True, 
                     db_names: Optional[List[str]] = None) -> str:
        """
        Maneja una consulta combinando RAG y Database agents
        
        Args:
            query: Consulta del usuario
            use_rag: Si True, usa el agente RAG
            use_db: Si True, usa el agente de base de datos
            db_names: Lista de nombres de bases de datos a consultar
                     Si es None, consulta todas las disponibles
            
        Returns:
            Respuesta final combinada
        """
        logger.info(f"Procesando consulta: {query}")
        
        rag_response = "No se consultó documentación"
        db_response = "No se consultó base de datos"
        
        # Determinar tipo de consulta si no se especifican agentes
        if use_rag is None and use_db is None:
            query_type = self._determine_query_type(query)
            use_rag = query_type in ['documentation', 'both']
            use_db = query_type in ['database', 'both']
        
        # Consultar RAG si está habilitado
        if use_rag:
            try:
                rag_response = self.rag_agent.query_with_context(query)
                logger.info("Consulta RAG completada")
            except Exception as e:
                logger.error(f"Error en consulta RAG: {str(e)}")
                rag_response = f"Error en búsqueda de documentación: {str(e)}"
        
        # Consultar bases de datos si está habilitado
        if use_db:
            try:
                # Si no se especifican bases de datos, usar todas
                db_names_to_query = db_names or list(self.db_agent.db_connections.keys())
                
                db_results = []
                for db_name in db_names_to_query:
                    try:
                        result = self.db_agent.query_with_context(db_name, query)
                        if result and result != f"No se encontraron resultados para: {query}":
                            db_results.append(f"[{db_name}]\n{result}")
                    except Exception as e:
                        logger.error(f"Error consultando {db_name}: {str(e)}")
                        db_results.append(f"[{db_name}] Error: {str(e)}")
                
                db_response = "\n\n".join(db_results) if db_results else "No se encontraron resultados en bases de datos"
                logger.info("Consulta a bases de datos completada")
            except Exception as e:
                logger.error(f"Error en consulta a bases de datos: {str(e)}")
                db_response = f"Error en consulta a bases de datos: {str(e)}"
        
        # Combinar resultados
        return self._combine_results(rag_response, db_response, query)
    
    def handle_documentation_query(self, query: str) -> str:
        """
        Maneja una consulta que solo requiere documentación
        
        Args:
            query: Consulta del usuario
            
        Returns:
            Respuesta basada solo en documentación
        """
        return self.handle_query(query, use_rag=True, use_db=False)
    
    def handle_database_query(self, query: str, db_name: str) -> str:
        """
        Maneja una consulta que solo requiere base de datos
        
        Args:
            query: Consulta del usuario
            db_name: Nombre de la base de datos a consultar
            
        Returns:
            Respuesta basada solo en base de datos
        """
        return self.handle_query(query, use_rag=False, use_db=True, db_names=[db_name])
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado del sistema (para monitoreo)
        
        Returns:
            Diccionario con información del estado
        """
        status = {
            "rag_agent": {
                "collection_info": self.rag_agent.get_collection_info()
            },
            "db_agent": {
                "connections": list(self.db_agent.db_connections.keys())
            }
        }
        
        return status
    
    def initialize_from_scratch(self, pdf_dir: str, db_paths: Dict[str, str]) -> int:
        """
        Inicializa el sistema desde cero con nuevos datos
        
        Args:
            pdf_dir: Directorio con PDFs para indexar
            db_paths: Diccionario con rutas a bases de datos
                     Ejemplo: {"maintenance": "data/maintenance.db"}
            
        Returns:
            Número total de chunks procesados
        """
        # Procesar PDFs
        chunks_processed = self.rag_agent.load_pdfs(pdf_dir)
        
        # Añadir conexiones a bases de datos
        for db_name, db_path in db_paths.items():
            self.db_agent.add_connection(db_name, db_path)
        
        return chunks_processed
