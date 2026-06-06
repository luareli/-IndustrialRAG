# API Reference - IndustrialKnowledgeAgent

> Referencia de la API de los agentes

---

## 📋 Clases Principales

### WorkflowOrchestrator

**Ubicacion:** `IndustrialRAG.agents.orchestrator.WorkflowOrchestrator`

**Constructor:**
```python
WorkflowOrchestrator(rag_agent: RAGAgent, db_agent: DatabaseQueryAgent)
```

**Metodos:**

| Metodo | Descripcion | Parametros | Retorno |
|--------|-------------|------------|---------|
| `handle_query(query, use_rag=True, use_db=True, db_names=None)` | Maneja consulta combinada | query: str, use_rag: bool, use_db: bool, db_names: List[str] | str |
| `handle_documentation_query(query)` | Solo RAG | query: str | str |
| `handle_database_query(query, db_name)` | Solo Database | query: str, db_name: str | str |
| `get_system_status()` | Estado del sistema | - | dict |
| `initialize_from_scratch(pdf_dir, db_paths)` | Reinicializar | pdf_dir: str, db_paths: dict | int |

**Ejemplo:**
```python
from IndustrialRAG.main import initialize_system

orchestrator = initialize_system()
response = orchestrator.handle_query("Procedimiento para compresor")
```

---

### RAGAgent

**Ubicacion:** `IndustrialRAG.agents.rag_agent.RAGAgent`

**Constructor:**
```python
RAGAgent(chroma_client: chromadb.Client, collection_name: str = None)
```

**Metodos:**

| Metodo | Descripcion | Parametros | Retorno |
|--------|-------------|------------|---------|
| `load_pdfs(pdf_dir)` | Cargar PDFs | pdf_dir: str | int |
| `search(query, top_k=3)` | Buscar documentos | query: str, top_k: int | dict |
| `generate_response(query, context=None)` | Generar respuesta | query: str, context: str | str |
| `query_with_context(query, top_k=3)` | Buscar + Generar | query: str, top_k: int | str |
| `get_collection_info()` | Info coleccion | - | dict |

**Ejemplo:**
```python
from IndustrialRAG.agents.rag_agent import RAGAgent
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
rag_agent = RAGAgent(client)
rag_agent.load_pdfs("./documentos/")
results = rag_agent.search("mantenimiento compresor", top_k=5)
```

---

### DatabaseQueryAgent

**Ubicacion:** `IndustrialRAG.agents.database_agent.DatabaseQueryAgent`

**Constructor:**
```python
DatabaseQueryAgent(db_connections: Dict[str, sqlite3.Connection] = None)
```

**Metodos:**

| Metodo | Descripcion | Parametros | Retorno |
|--------|-------------|------------|---------|
| `add_connection(db_name, db_path)` | Anadir conexion | db_name: str, db_path: str | None |
| `get_schema(db_name, table_name=None)` | Obtener esquema | db_name: str, table_name: str | str |
| `generate_sql_query(user_query, db_schema, db_name)` | Generar SQL | user_query: str, db_schema: str, db_name: str | str |
| `query_database(db_name, sql_query, params=())` | Ejecutar SQL | db_name: str, sql_query: str, params: tuple | List[dict] |
| `natural_query(db_name, user_query, table_name=None)` | Consulta natural | db_name: str, user_query: str, table_name: str | List[dict] |
| `query_with_context(db_name, user_query)` | Consulta + contexto | db_name: str, user_query: str | str |
| `close_all_connections()` | Cerrar conexiones | - | None |

**Ejemplo:**
```python
from IndustrialRAG.agents.database_agent import DatabaseQueryAgent

db_agent = DatabaseQueryAgent()
db_agent.add_connection("maintenance", "./data/maintenance.db")
results = db_agent.natural_query("maintenance", "Historial de EQ-001")
```

---

## 🔧 Utilidades

### Text Processor

**Ubicacion:** `IndustrialRAG.utils.text_processor`

| Funcion | Descripcion | Parametros | Retorno |
|---------|-------------|------------|---------|
| `clean_text(text)` | Limpieza de texto | text: str | str |
| `extract_pdf_text(pdf_path)` | Extraer texto PDF | pdf_path: Path | str |
| `chunk_text(text, chunk_size, overlap)` | Dividir en chunks | text: str, chunk_size: int, overlap: int | List[str] |
| `process_pdf_to_chunks(pdf_path, ...)` | PDF -> chunks | pdf_path: Path, ... | List[str] |

### Database Utils

**Ubicacion:** `IndustrialRAG.utils.database_utils`

| Funcion | Descripcion | Parametros | Retorno |
|---------|-------------|------------|---------|
| `create_db_connection(db_path)` | Crear conexion | db_path: str | sqlite3.Connection |
| `get_table_schema(conn, table_name)` | Obtener esquema | conn: Connection, table_name: str | str |
| `get_all_table_schemas(conn)` | Todos los esquemas | conn: Connection | str |
| `sanitize_sql_query(query)` | Validar SQL | query: str | bool |
| `safe_execute_query(conn, query, params)` | Ejecutar SQL segura | conn: Connection, query: str, params: tuple | List[dict] |
| `initialize_database(db_path, schema)` | Inicializar DB | db_path: str, schema: str | Connection |

---

## 📁 Configuracion

**Ubicacion:** `IndustrialRAG.config.settings`

**Clases:**

```python
ChromaConfig(path, collection_name, embedding_model, chunk_size, chunk_overlap)
MistralConfig(api_key, model, temperature, max_tokens)
DatabaseConfig(maintenance_db, specs_db, inventory_db)
AppConfig(chroma, mistral, database)

load_config() -> AppConfig
```

---

## 🎯 Datos de Retorno

### RAGAgent.search()
```python
{
    "contexts": [str, ...],      # Textos de documentos
    "metadatas": [dict, ...],   # Metadatos de cada documento
    "distances": [float, ...],  # Distancias (similaridad)
    "ids": [str, ...]           # IDs de documentos
}
```

### DatabaseQueryAgent.natural_query()
```python
[
    {"col1": val1, "col2": val2, ...},  # Fila 1
    {"col1": val1, "col2": val2, ...},  # Fila 2
    ...
]
```

### WorkflowOrchestrator.get_system_status()
```python
{
    "rag_agent": {
        "collection_info": {
            "name": str,
            "count": int
        }
    },
    "db_agent": {
        "connections": [str, ...]
    }
}
```

---

## 📖 Ejemplos Completos

### Ejemplo 1: Sistema de Tickets
```python
from IndustrialRAG.main import initialize_system

orchestrator = initialize_system()

def crear_ticket(equipo_id, problema):
    info = orchestrator.handle_query(f"Info del equipo {equipo_id}")
    procedimiento = orchestrator.handle_query(f"Procedimiento para {problema}")
    historial = orchestrator.handle_database_query(
        f"Historial de {equipo_id}", db_name="maintenance"
    )
    return {"equipo": equipo_id, "problema": problema, 
            "info": info, "procedimiento": procedimiento, "historial": historial}
```

### Ejemplo 2: Generar Informe
```python
def generar_informe(equipo_id, fecha_inicio, fecha_fin):
    logs = orchestrator.db_agent.query_database(
        "maintenance",
        "SELECT * FROM maintenance_logs WHERE equipment_id = ? AND maintenance_date BETWEEN ? AND ?",
        (equipo_id, fecha_inicio, fecha_fin)
    )
    procedimientos = orchestrator.handle_documentation_query(
        f"Procedimientos para {equipo_id}"
    )
    return f"Informe para {equipo_id}:\n\n{procedimientos}\n\n{logs}"
```

---

**Siguiente:** [Seguridad](SEGURIDAD.md)
