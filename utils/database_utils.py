"""
Utilidades para manejo seguro de bases de datos SQLite
"""
import sqlite3
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


def create_db_connection(db_path: str) -> sqlite3.Connection:
    """Crea una conexión segura a SQLite"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_table_schema(conn: sqlite3.Connection, table_name: str) -> Optional[str]:
    """Obtiene el esquema de una tabla en formato legible"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        if not columns:
            return None
        
        schema_parts = []
        for col in columns:
            col_name = col['name']
            col_type = col['type']
            not_null = " NOT NULL" if col['notnull'] else ""
            pk = " PRIMARY KEY" if col['pk'] else ""
            default = f" DEFAULT {col['dflt_value']}" if col['dflt_value'] else ""
            schema_parts.append(f"{col_name} {col_type}{not_null}{pk}{default}")
        
        return f"Table: {table_name} (columns: {', '.join(schema_parts)})"
    except sqlite3.Error as e:
        return f"Error obteniendo esquema: {str(e)}"


def get_all_table_schemas(conn: sqlite3.Connection) -> str:
    """Obtiene todos los esquemas de tablas en la base de datos"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row['name'] for row in cursor.fetchall()]
    
    schemas = []
    for table in tables:
        schema = get_table_schema(conn, table)
        if schema:
            schemas.append(schema)
    
    return "\n".join(schemas)


def sanitize_sql_query(query: str) -> bool:
    """
    Verifica si una consulta SQL es potencialmente peligrosa
    
    Args:
        query: Consulta SQL a validar
        
    Returns:
        True si la consulta parece segura, False si es sospechosa
    """
    # Patrones sospechosos
    dangerous_patterns = [
        r'\bDROP\b',
        r'\bDELETE\b',
        r'\bTRUNCATE\b',
        r'\bALTER\b',
        r'\bINSERT\b',
        r'\bUPDATE\b',
        r'\bEXEC\b',
        r'\bUNION\b.*\bSELECT\b',
        r';.*--',
        r'\bXP_\w+',
        r'\bEXECUTE\b',
        r'\bDECLARE\b',
    ]
    
    query_upper = query.upper()
    for pattern in dangerous_patterns:
        if re.search(pattern, query_upper, re.IGNORECASE):
            return False
    
    return True


def safe_execute_query(conn: sqlite3.Connection, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """
    Ejecuta una consulta SQL de forma segura con parámetros
    
    Args:
        conn: Conexión a la base de datos
        query: Consulta SQL
        params: Parámetros para la consulta
        
    Returns:
        Lista de diccionarios con los resultados
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise ValueError(f"Error en consulta SQL: {str(e)}")


def initialize_database(db_path: str, schema: str) -> sqlite3.Connection:
    """
    Inicializa una base de datos con un esquema dado
    
    Args:
        db_path: Ruta a la base de datos
        schema: Esquema SQL para crear tablas
        
    Returns:
        Conexión a la base de datos inicializada
    """
    conn = create_db_connection(db_path)
    
    try:
        cursor = conn.cursor()
        for statement in schema.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
        conn.commit()
    except sqlite3.Error as e:
        conn.rollback()
        raise ValueError(f"Error inicializando base de datos: {str(e)}")
    
    return conn
