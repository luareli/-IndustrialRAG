"""
Configuración centralizada del IndustrialKnowledgeAgent con Chroma
"""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class ChromaConfig:
    """Configuración para Chroma Vector Database"""
    path: str = "./chroma_db"
    collection_name: str = "industrial_docs"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass
class MistralConfig:
    """Configuración para Mistral AI"""
    api_key: Optional[str] = None
    model: str = "mistral-small-latest"
    temperature: float = 0.1
    max_tokens: int = 4096


@dataclass
class DatabaseConfig:
    """Configuración para bases de datos SQLite"""
    maintenance_db: str = "data/maintenance_db.sqlite"
    specs_db: str = "data/technical_specifications_db.sqlite"
    inventory_db: str = "data/inventory_db.sqlite"


@dataclass
class AppConfig:
    """Configuración principal de la aplicación"""
    chroma: ChromaConfig = ChromaConfig()
    mistral: MistralConfig = MistralConfig()
    database: DatabaseConfig = DatabaseConfig()


def load_config() -> AppConfig:
    """Carga la configuración desde variables de entorno"""
    config = AppConfig()
    
    # Cargar API key de Mistral
    mistral_api_key = os.environ.get("MISTRAL_API_KEY")
    if not mistral_api_key:
        raise ValueError("MISTRAL_API_KEY no esta configurada en las variables de entorno")
    config.mistral.api_key = mistral_api_key
    
    # Crear directorios si no existen
    Path(config.chroma.path).mkdir(parents=True, exist_ok=True)
    Path(config.database.maintenance_db).parent.mkdir(parents=True, exist_ok=True)
    Path(config.database.specs_db).parent.mkdir(parents=True, exist_ok=True)
    Path(config.database.inventory_db).parent.mkdir(parents=True, exist_ok=True)
    
    return config


# Instancia global de configuración
config = load_config()