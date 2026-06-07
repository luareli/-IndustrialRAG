# Arquitectura Tecnica - IndustrialRAG

> Detalles de implementacion del sistema RAG

---

## 🏗️ Vista General

```
                    INDUSTRIAL KNOWLEDGE AGENT
┌─────────────────────────────────────────────────────────────┐
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  RAGAgent    │  │ DatabaseQueryAgent│  │ WorkflowOrchestrator│ │
│  │ (Chroma+PDF) │  │   (SQLite)       │  │   (Combina)      │ │
│  └──────┬──────┘  └─────────┬─────────┘  └──────────┬────────┘ │
│         │                   │                      │            │
│         ▼                   ▼                      ▼            │
│  ┌─────────────┐     ┌─────────────┐      ┌─────────────┐  │
│  │  Chroma DB  │     │ SQLite DB   │      │  Mistral AI │  │
│  │ (Vectores)   │     │ (Estructura)│      │ (LLM)       │  │
│  └─────────────┘     └─────────────┘      └─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Componentes

### 1. WorkflowOrchestrator
**Archivo:** `agents/orchestrator.py`
- Deteccion automatica de tipo de consulta (doc/DB/both)
- Coordination entre agentes
- Combinacion de resultados

### 2. RAGAgent
**Archivo:** `agents/rag_agent.py`
- Carga PDFs -> Chroma
- Busqueda vectorial
- Generacion de respuestas con contexto

### 3. DatabaseQueryAgent
**Archivo:** `agents/database_agent.py`
- Conexiones SQLite
- Generacion SQL segura desde lenguaje natural
- Proteccion contra SQL injection

---

## 📁 Flujo de Datos

```
User Query
    │
    ▼
Determinar Tipo (doc_keywords vs db_keywords)
    │
    ├──▶ RAGAgent (si use_rag)
    │       │
    │       ▼
    │    Chroma.query() → Contextos
    │
    └──▶ DatabaseQueryAgent (si use_db)
            │
            ▼
         SQL Generation + Validation → Resultados
    │
    └──────────▶ Combinar Resultados → Mistral AI → Respuesta Final
```

---

## 🔧 Configuracion

### Estructura de Configuracion (`config/settings.py`)

```python
@dataclass
class ChromaConfig:
    path: str = "./chroma_db"
    collection_name: str = "industrial_docs"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 1000
    chunk_overlap: int = 200

@dataclass  
class MistralConfig:
    model: str = "mistral-small-latest"
    temperature: float = 0.1
    max_tokens: int = 4096

@dataclass
class DatabaseConfig:
    maintenance_db: str = "data/maintenance_db.sqlite"
    specs_db: str = "data/technical_specifications_db.sqlite"

@dataclass
class AppConfig:
    chroma: ChromaConfig
    mistral: MistralConfig
    database: DatabaseConfig
```

---

## 🔒 Seguridad

### Proteccion contra SQL Injection

1. **Generacion segura:** Prompt estricto "SOLO SELECT"
2. **Validacion:** `sanitize_sql_query()` + verificacion de patrones
3. **Ejecucion:** Parametros vinculados con `sqlite3`

### Flujo de Validacion
```
User Query → Generar SQL (Mistral) → Validar SELECT → Validar patrones → Ejecutar/Cancelar
```

---

## 📊 Utilidades

### Text Processor (`utils/text_processor.py`)
- `clean_text()`: Limpieza de caracteres
- `extract_pdf_text()`: Extraccion con PyPDF
- `chunk_text()`: Sliding window con overlap

### Database Utils (`utils/database_utils.py`)
- `sanitize_sql_query()`: Validacion de consultas
- `safe_execute_query()`: Ejecucion con parametros
- `get_table_schema()`: Obtener esquema

---

## ⚡ Rendimiento

| Operacion | Tiempo Estimado | Factores |
|-----------|-----------------|----------|
| Cargar 100 PDFs | 2-5 min | CPU, tamano PDFs |
| Busqueda vectorial | 100-500ms | SSD, tamano collection |
| Generar respuesta | 500-2000ms | Mistral API |
| Consulta SQLite | 10-100ms | Tamano DB |

---

## 🔄 Escalabilidad

### Horizontal (Multiples usuarios)
- Chroma Server (Docker) para multiples clientes
- SQLite WAL mode para concurrencia

### Vertical (Datasets grandes)
- Multiple colecciones por tipo
- Aumentar chunk_size (1500-2000)
- Cachear consultas frecuentes

---

## 📚 Referencias
- [Chroma Docs](https://docs.trychroma.com/)
- [Mistral AI Docs](https://docs.mistral.ai/)
- [Sentence Transformers](https://www.sbert.net/)

---

**Siguiente:** [API Reference](API.md)
