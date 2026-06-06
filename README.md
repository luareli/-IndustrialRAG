# IndustrialKnowledgeAgent con Chroma

> **Sistema RAG para Mantenimiento Industrial**
> Usa Chroma como vector database + Mistral AI como LLM + SQLite para datos estructurados

---

## 📋 Descripción General

**IndustrialKnowledgeAgent** es un sistema de **Retrieval-Augmented Generation (RAG)** especializado en mantenimiento industrial que combina:

- **Búsqueda vectorial** en documentación técnica (PDFs) mediante **Chroma**
- **Consultas a bases de datos** SQLite (historial de mantenimiento, especificaciones, inventario)
- **Generación de respuestas** con **Mistral AI**
- **Orquestación inteligente** que combina ambas fuentes de información

El sistema está diseñado para responder consultas técnicas como:
- "¿Cuál es el procedimiento de mantenimiento para el compresor de aire?"
- "Muestra el historial de mantenimiento del equipo EQ-001"
- "¿Cuáles son las especificaciones técnicas del generador GEN-100KW?"

---

## 🏗️ Arquitectura

```mermaid
graph TD
    subgraph IndustrialKnowledgeAgent["IndustrialKnowledgeAgent"]
        direction TB
        User((User)) -->|Query| Orchestrator
        RAG[RAGAgent\n(Chroma + PDFs)] --> Orchestrator
        DB[DatabaseQueryAgent\n(SQLite)] --> Orchestrator

        Orchestrator[WorkflowOrchestrator] -->|Vector Search| ChromaDB[(Chroma DB\nVector Store)]
        Orchestrator -->|SQL Queries| SQLiteDB[(SQLite DB\nStructured)]
    end

    style IndustrialKnowledgeAgent fill:#f8f9fa,stroke:#6c757d,stroke-width:2px
    style Orchestrator fill:#e3f2fd,stroke:#2196f3,stroke-width:2px
    style RAG fill:#e8f5e9,stroke:#4caf50,stroke-width:2px
    style DB fill:#ffebee,stroke:#f44336,stroke-width:2px
    style ChromaDB fill:#fff3e0,stroke:#ff9800,stroke-width:2px
    style SQLiteDB fill:#f3e5f5,stroke:#9c27b0,stroke-width:2px
    style User fill:#ffffff,stroke:#6c757d,stroke-width:2px
```

### Componentes

| Componente | Responsabilidad | Tecnologías |
|------------|-----------------|-------------|
| `RAGAgent` | Indexación y búsqueda en PDFs | Chroma, SentenceTransformer, PyPDF |
| `DatabaseQueryAgent` | Consultas seguras a bases de datos | SQLite, Mistral AI (SQL generation) |
| `WorkflowOrchestrator` | Integración y orquestación | Mistral AI (response combination) |

---

## 📦 Requisitos Previos

### Sistema Operativo
- Linux (recomendado)
- macOS
- Windows 10/11

### Python
- **Versión requerida:** Python 3.9 o superior

### Dependencias
Ver [requirements.txt](requirements.txt) para la lista completa.

**Dependencias principales:**
- `mistralai>=1.5.1` - Cliente para Mistral AI
- `chromadb==0.5.0` - Vector database
- `sentence-transformers>=2.2.2` - Embeddings (all-MiniLM-L6-v2)
- `pypdf==4.0.0` - Procesamiento de PDFs
- `sqlite3` - Base de datos (incluida en Python estándar)

---

## ⚙️ Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd IndustrialRAG
```

### 2. Crear entorno virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# O en Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Instalar dependencias opcionales (para ejemplos)

```bash
pip install fpdf2  # Para generar PDFs de ejemplo
```

### 5. Configurar API Key de Mistral

El sistema requiere una API key de Mistral AI para funcionar:

```bash
export MISTRAL_API_KEY="tu_api_key_de_mistral"
```

> **📌 ¿Cómo obtener una API key?**
> 1. Ve a [Mistral AI Console](https://console.mistral.ai/api-keys/)
> 2. Inicia sesión con tu cuenta
> 3. Genera una nueva API key
> 4. Copia el valor y configúralo como variable de entorno

**Para Windows (PowerShell):**
```powershell
$env:MISTRAL_API_KEY = "tu_api_key_de_mistral"
```

**Para Windows (CMD):**
```cmd
set MISTRAL_API_KEY=tu_api_key_de_mistral
```

---

## 🚀 Uso Rápido

### Ejecución básica

```bash
python3 main.py
```

Este comando:
1. Crea bases de datos SQLite de ejemplo
2. Genera un PDF de ejemplo con documentación técnica
3. Indexa los PDFs en Chroma
4. Ejecuta 4 consultas de demostración

### Personalización

#### 1. Cargar tus propios PDFs

Organiza tus documentos PDF en un directorio y carga el sistema:

```python
from IndustrialRAG.main import initialize_system

# Inicializar con tus PDFs
orchestrator = initialize_system(
    pdf_dir="/ruta/a/tus/pdf",
    db_paths={
        "maintenance": "/ruta/a/tu/base_de_datos.sqlite"
    }
)

# Realizar una consulta
response = orchestrator.handle_query(
    "¿Cuál es el procedimiento de mantenimiento para el equipo XYZ?"
)
print(response)
```

#### 2. Consultar solo documentación

```python
response = orchestrator.handle_documentation_query(
    "¿Qué normativas aplican al mantenimiento de compresores?"
)
```

#### 3. Consultar solo base de datos

```python
response = orchestrator.handle_database_query(
    "Muestra el historial del equipo EQ-001",
    db_name="maintenance"
)
```

---

## 🔧 Configuración Avanzada

### Configuración mediante variables de entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `MISTRAL_API_KEY` | API key de Mistral AI | *Requerido* |
| `CHROMA_PATH` | Ruta a la base de datos Chroma | `./chroma_db` |
| `CHROMA_COLLECTION` | Nombre de la colección | `industrial_docs` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `all-MiniLM-L6-v2` |

### Configuración en código

Edita `config/settings.py` para personalizar:

```python
from IndustrialRAG.config.settings import ChromaConfig, MistralConfig, DatabaseConfig, AppConfig

config = AppConfig(
    chroma=ChromaConfig(
        path="./mi_chroma_db",
        collection_name="mis_documentos",
        embedding_model="BAAI/bge-small-en-v1.5",  # Alternativa
        chunk_size=1500,
        chunk_overlap=300
    ),
    mistral=MistralConfig(
        model="mistral-medium-latest",  # Modelo más potente
        temperature=0.3,
        max_tokens=2048
    ),
    database=DatabaseConfig(
        maintenance_db="./data/mi_mantenimiento.db"
    )
)
```

---

## 📊 Bases de Datos de Ejemplo

El sistema incluye esquemas predefinidos para:

### 1. Base de datos de mantenimiento (`maintenance_db.sqlite`)

**Tablas:**
- `equipment` - Información de equipos
- `maintenance_logs` - Historial de mantenimientos

**Esquema:**
```sql
-- Tabla de equipos
CREATE TABLE equipment (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    model TEXT,
    manufacturer TEXT,
    installation_date TEXT,
    last_maintenance TEXT,
    status TEXT DEFAULT 'ACTIVE'
);

-- Tabla de registros de mantenimiento
CREATE TABLE maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id TEXT NOT NULL,
    equipment_name TEXT NOT NULL,
    maintenance_date TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'COMPLETED',
    technician TEXT,
    cost REAL DEFAULT 0.0
);
```

### 2. Base de datos de especificaciones (`technical_specifications_db.sqlite`)

**Tablas:**
- `technical_specs` - Especificaciones técnicas de equipos
- `safety_protocols` - Protocolos de seguridad

---

## 🔒 Seguridad

### Protección contra SQL Injection

El sistema implementa múltiples capas de protección:

1. **Generación de SQL segura:**
   - El LLM genera solo consultas SELECT
   - Validación de que no contienen palabras clave peligrosas (DROP, DELETE, INSERT, etc.)
   - Temperatura 0.0 para precisión máxima

2. **Sanitización de consultas:**
   - Función `sanitize_sql_query()` verifica patrones sospechosos
   - Solo se ejecutan consultas que pasan todas las validaciones

3. **Uso de parámetros:**
   - Las consultas pueden usar parámetros con `?`
   - Ejecución segura mediante `sqlite3` con parámetros vinculados

### Manejo de errores

Todos los componentes incluyen:
- Try-catch en operaciones críticas
- Logging detallado de errores
- Respuestas gracefully degradadas

---

## 📁 Estructura del Proyecto

```
IndustrialRAG/
├── agents/
│   ├── __init__.py
│   ├── rag_agent.py            # Agente RAG con Chroma
│   ├── database_agent.py       # Agente de base de datos
│   └── orchestrator.py         # Orquestador
├── config/
│   ├── __init__.py
│   └── settings.py             # Configuración centralizada
├── utils/
│   ├── __init__.py
│   ├── text_processor.py       # Procesamiento de texto
│   └── database_utils.py       # Utilidades de base de datos
├── data/                      # Datos (generados en ejecución)
├── docs/                      # Documentación
├── main.py                    # Punto de entrada
├── requirements.txt           # Dependencias
└── __init__.py
```

---

## 🧪 Pruebas

### Ejecutar ejemplos integrados

```bash
python3 main.py
```

### Pruebas manuales

```python
from IndustrialRAG.main import initialize_system

# Inicializar
orchestrator = initialize_system()

# Probar diferentes tipos de consultas
queries = [
    "¿Qué procedimientos de seguridad debo seguir?",
    "Muestra el historial de EQ-001",
    "Especificaciones del compresor",
    "¿Cuál es el costo total de mantenimiento este año?"
]

for query in queries:
    response = orchestrator.handle_query(query)
    print(f"Q: {query}")
    print(f"A: {response[:200]}...")
    print("---")
```

---

## 📚 Documentación Adicional

- [Guía de Instalación](docs/INSTALACION.md) - Instrucciones detalladas de instalación
- [Guía de Uso](docs/USO.md) - Cómo usar el sistema en producción
- [Arquitectura Técnica](docs/ARQUITECTURA.md) - Detalles de implementación
- [API Reference](docs/API.md) - Referencia de la API de los agentes
- [Seguridad](docs/SEGURIDAD.md) - Medidas de seguridad implementadas
- [Solución de Problemas](docs/TROUBLESHOOTING.md) - Problemas comunes y soluciones

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios
4. Ejecuta pruebas si existen
5. Envía un Pull Request

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 🙏 Agradecimientos

- [Mistral AI](https://mistral.ai/) - Por el modelo de lenguaje
- [Chroma](https://www.trychroma.com/) - Por el vector database
- [Sentence Transformers](https://www.sbert.net/) - Por los embeddings

---

## 📞 Soporte

Para problemas o preguntas:

1. Consulta la [documentación](docs/)
2. Revisa los [problemas abiertos](https://github.com/...) (si aplica)
3. Crea un nuevo issue con una descripción detallada
