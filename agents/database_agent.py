"""
DatabaseQueryAgent: Agente para consultas seguras a bases de datos SQLite
"""
import logging
import json
from typing import Dict, List, Any, Optional
import sqlite3

# Compatibilidad con mistralai 1.x y 2.x
try:
    from mistralai import Mistral
except ImportError:
    try:
        from mistralai.client import MistralClient as Mistral
    except ImportError:
        raise ImportError("mistralai no está instalado o la versión no es compatible (requiere >=1.2.0,>=2.0.0)")

from config.settings import config
from utils.database_utils import (
    create_db_connection,
    get_table_schema,
    get_all_table_schemas,
    safe_execute_query,
    sanitize_sql_query
)


logger = logging.getLogger(__name__)


class DatabaseQueryAgent:
    """
    Agente que consulta bases de datos SQLite de forma segura
    """
    
    def __init__(self, db_connections: Dict[str, sqlite3.Connection] = None):
        """
        Inicializa el DatabaseQueryAgent
        
        Args:
            db_connections: Diccionario con conexiones a bases de datos
                           Ejemplo: {"maintenance": conn1, "specs": conn2}
        """
        self.db_connections = db_connections or {}
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
    
    def add_connection(self, db_name: str, db_path: str) -> None:
        """
        Añade una nueva conexión a base de datos
        
        Args:
            db_name: Nombre para identificar la base de datos
            db_path: Ruta al archivo SQLite
        """
        try:
            self.db_connections[db_name] = create_db_connection(db_path)
            logger.info(f"Conexión añada: {db_name} -> {db_path}")
        except Exception as e:
            logger.error(f"Error añadiendo conexión {db_name}: {str(e)}")
            raise
    
    def get_schema(self, db_name: str, table_name: Optional[str] = None) -> str:
        """
        Obtiene el esquema de una tabla o de toda la base de datos
        
        Args:
            db_name: Nombre de la base de datos
            table_name: Nombre de la tabla (opcional). Si es None, devuelve todos los esquemas
            
        Returns:
            Descripción del esquema
        """
        if db_name not in self.db_connections:
            raise ValueError(f"Base de datos {db_name} no encontrada")
        
        conn = self.db_connections[db_name]
        
        if table_name:
            return get_table_schema(conn, table_name) or f"Tabla {table_name} no encontrada"
        else:
            return get_all_table_schemas(conn)
    
    def generate_sql_query(self, user_query: str, db_schema: str, db_name: str = "unknown") -> str:
        """
        Genera una consulta SQL segura a partir de una consulta en lenguaje natural
        
        Args:
            user_query: Consulta en lenguaje natural
            db_schema: Esquema de la base de datos
            db_name: Nombre de la base de datos (para contexto)
            
        Returns:
            Consulta SQL generada
        """
        prompt = f"""Eres un experto en SQL y bases de datos industriales.
        Genera UNICAMENTE una consulta SQL de SOLO LECTURA (SELECT) basada en la siguiente información.
        
        Reglas estrictas:
        1. NUNCA uses DROP, DELETE, INSERT, UPDATE, ALTER, TRUNCATE, EXEC, EXECUTE, DECLARE
        2. NUNCA uses concatenación de strings con entrada de usuario
        3. Usa parámetros con ? si es necesario filtrar por valores
        4. Solo genera consultas SELECT
        5. Si no puedes generar una consulta segura, devuelve: "NO_PUEDO_GENERAR_CONSULTA_SEGURA"
        
        Base de datos: {db_name}
        Esquema:
        {db_schema}
        
        Consulta del usuario: {user_query}
        
        Genera SOLAMENTE la consulta SQL, sin explicaciones adicionales:"""
        
        try:
            response = self._chat_method(
                model=config.mistral.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,  # Temperatura baja para precisión
                max_tokens=512
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Limpiar formato de código (backticks, markdown, etc.)
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            # Validación de seguridad
            if "NO_PUEDO_GENERAR_CONSULTA_SEGURA" in sql_query:
                return ""
            
            # Verificar que sea una consulta SELECT
            sql_query_upper = sql_query.upper().strip()
            if not sql_query_upper.startswith("SELECT"):
                logger.warning(f"Consulta no es SELECT: {sql_query}")
                return ""
            
            # Validar con patrones peligrosos
            if not sanitize_sql_query(sql_query):
                logger.warning(f"Consulta SQL sospechosa: {sql_query}")
                return ""
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generando SQL: {str(e)}")
            return ""
    
    def query_database(self, db_name: str, sql_query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL en una base de datos específica
        
        Args:
            db_name: Nombre de la base de datos
            sql_query: Consulta SQL a ejecutar
            params: Parámetros para la consulta
            
        Returns:
            Lista de diccionarios con los resultados
        """
        if db_name not in self.db_connections:
            raise ValueError(f"Base de datos {db_name} no encontrada")
        
        conn = self.db_connections[db_name]
        
        try:
            return safe_execute_query(conn, sql_query, params)
        except Exception as e:
            logger.error(f"Error en consulta a {db_name}: {str(e)}")
            raise ValueError(f"Error en consulta SQL: {str(e)}")
    
    def natural_query(self, db_name: str, user_query: str, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta en lenguaje natural y devuelve los resultados
        
        Args:
            db_name: Nombre de la base de datos
            user_query: Consulta en lenguaje natural
            table_name: Nombre de la tabla (opcional, para obtener esquema específico)
            
        Returns:
            Lista de diccionarios con los resultados
        """
        # Obtener esquema
        if table_name:
            schema = self.get_schema(db_name, table_name)
        else:
            schema = self.get_schema(db_name)
        
        # Generar SQL
        sql_query = self.generate_sql_query(user_query, schema, db_name)
        
        if not sql_query:
            logger.warning(f"No se pudo generar consulta SQL segura para: {user_query}")
            return []
        
        logger.info(f"Consulta SQL generada: {sql_query}")
        
        # Ejecutar consulta
        try:
            return self.query_database(db_name, sql_query)
        except Exception as e:
            logger.error(f"Error ejecutando consulta: {str(e)}")
            return []
    
    def query_with_context(self, db_name: str, user_query: str) -> str:
        """
        Ejecuta una consulta y devuelve los resultados en formato legible
        
        Args:
            db_name: Nombre de la base de datos
            user_query: Consulta en lenguaje natural
            
        Returns:
            String con resultados en formato JSON o mensaje de error
        """
        results = self.natural_query(db_name, user_query)
        
        if not results:
            return f"No se encontraron resultados para: {user_query}"
        
        return json.dumps(results, indent=2, ensure_ascii=False)
    
    def close_all_connections(self) -> None:
        """Cierra todas las conexiones a bases de datos"""
        for db_name, conn in self.db_connections.items():
            try:
                conn.close()
                logger.info(f"Conexión cerrada: {db_name}")
            except Exception as e:
                logger.error(f"Error cerrando conexión {db_name}: {str(e)}")
        
        self.db_connections = {}
    
    def __del__(self):
        """Destructor: cierra conexiones al eliminar el objeto"""
        self.close_all_connections()
