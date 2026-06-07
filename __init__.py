"""
IndustrialKnowledgeAgent - Sistema RAG con Chroma y Mistral AI

Este paquete implementa un sistema de recuperacion-augmented generation (RAG)
para mantenimiento industrial, usando:
- Chroma como vector database
- Mistral AI como LLM
- SQLite para bases de datos estructuradas

Estructura:
- config/: Configuracion de la aplicacion
- agents/: Agentes RAG, Database y Orchestrator
- utils/: Utilidades de procesamiento de texto y bases de datos
- data/: Datos de ejemplo (PDFs y bases de datos)

Uso:
    from main import initialize_system
    
    orchestrator = initialize_system(
        pdf_dir="path/to/pdfs",
        db_paths={"maintenance": "path/to/maintenance.db"}
    )
    
    response = orchestrator.handle_query("Cual es el procedimiento de mantenimiento?")
"""

__version__ = "1.0.0"
__author__ = "Industrial RAG Team"
__license__ = "MIT"

# Exportar clases principales
from agents.rag_agent import RAGAgent
from agents.database_agent import DatabaseQueryAgent
from agents.orchestrator import WorkflowOrchestrator
from config.settings import config, load_config

__all__ = [
    'RAGAgent',
    'DatabaseQueryAgent',
    'WorkflowOrchestrator',
    'config',
    'load_config',
    '__version__',
    '__author__',
    '__license__'
]
