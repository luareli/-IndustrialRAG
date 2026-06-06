# Guía de Uso - IndustrialKnowledgeAgent

> Cómo usar el sistema en producción y desarrollo

---

## 🚀 Uso Básico

### Inicio rápido

El método más sencillo para empezar:

```bash
# Ejecutar el script principal
python3 IndustrialRAG/main.py
```

Esto:
1. Crea bases de datos de ejemplo
2. Genera un PDF de ejemplo
3. Indexa los documentos
4. Ejecuta consultas de demostración

---

## 📖 Casos de Uso Comunes

### 1. Consultar documentación técnica

```python
from IndustrialRAG.main import initialize_system

# Inicializar
orchestrator = initialize_system(pdf_dir="docs/tecnicos")

# Consultar procedimientos
response = orchestrator.handle_query(
    "¿Cuál es el procedimiento de mantenimiento para el compresor de aire?"
)
print(response)
```

**Salida esperada:**
```
El procedimiento de mantenimiento para el compresor de aire AX-5000 incluye:

1. Desconexión de la red eléctrica
2. Esperar 10 minutos para enfriamiento
3. Uso de EPI: guantes, gafas, calzado de seguridad
4. Verificar presión en cero
5. Cambio de filtros de aire cada 250 horas
6. Cambio de filtro de aceite cada 500 horas

Normativa aplicable: ISO 8573-1 para calidad de aire comprimido.
```

### 2. Consultar historial de mantenimiento

```python
# Con base de datos cargada
response = orchestrator.handle_query(
    "Muestra el historial de mantenimiento del equipo EQ-001"
)
print(response)
```

**Salida esperada:**
```
[maintenance]
[
  {
    "id": 1,
    "equipment_id": "EQ-001",
    "equipment_name": "Compresor de Aire",
    "maintenance_date": "2024-01-15",
    "description": "Cambio de filtros de aire y aceite",
    "status": "COMPLETED",
    "technician": "Juan Pérez",
    "cost": 250.0
  },
  {
    "id": 2,
    "equipment_id": "EQ-001",
    "equipment_name": "Compresor de Aire",
    "maintenance_date": "2024-03-20",
    "description": "Inspección general y lubricación",
    "status": "COMPLETED",
    "technician": "Carlos López",
    "cost": 180.0
  }
]
```

### 3. Consultar especificaciones técnicas

```python
response = orchestrator.handle_query(
    "¿Cuáles son las especificaciones técnicas del generador GEN-100KW?"
)
print(response)
```

### 4. Consultas combinadas (documentación + base de datos)

```python
response = orchestrator.handle_query(
    "Necesito saber el procedimiento de mantenimiento del compresor y su historial"
)
print(response)
```

---

## 🎯 Tipos de Consultas

El sistema detecta automáticamente el tipo de consulta:

| Tipo de Consulta | Palabras Clave | Agente Principal |
|------------------|----------------|------------------|
| Documentación | procedimiento, manual, guía, especificación, cómo | RAG |
| Base de datos | equipo, máquina, historial, registro, lista, enumera | Database |
| Combinada | ambos tipos | Ambos |

### Forzar tipo de consulta

```python
# Solo documentación
response = orchestrator.handle_documentation_query(
    "Explica el protocolo de seguridad"
)

# Solo base de datos
response = orchestrator.handle_database_query(
    "Muestra todos los equipos",
    db_name="maintenance"
)

# Ambos (por defecto)
response = orchestrator.handle_query(
    "Información completa sobre el compresor EQ-001"
)
```

---

## 🔧 Configuración Avanzada

### Personalizar la configuración

```python
from IndustrialRAG.config.settings import AppConfig, ChromaConfig, MistralConfig

# Configuración personalizada
config = AppConfig(
    chroma=ChromaConfig(
        path="./mi_chroma",
        collection_name="documentos_industriales",
        embedding_model="BAAI/bge-small-en-v1.5",
        chunk_size=1200,
        chunk_overlap=250
    ),
    mistral=MistralConfig(
        model="mistral-medium-latest",
        temperature=0.2,
        max_tokens=2048
    )
)
```

### Usar múltiples colecciones de Chroma

```python
import chromadb
from IndustrialRAG.agents.rag_agent import RAGAgent

# Cliente Chroma
client = chromadb.PersistentClient(path="./chroma_db")

# Crear agente para colección específica
rag_agent_manuales = RAGAgent(client, "manuales_tecnicos")
rag_agent_normativas = RAGAgent(client, "normativas")

# Cargar documentos
rag_agent_manuales.load_pdfs("docs/manuales/")
rag_agent_normativas.load_pdfs("docs/normativas/")
```

### Conectar múltiples bases de datos

```python
from IndustrialRAG.agents.database_agent import DatabaseQueryAgent

db_agent = DatabaseQueryAgent()

# Añadir conexiones
db_agent.add_connection("mantenimiento", "data/maintenance.db")
db_agent.add_connection("especificaciones", "data/specs.db")
db_agent.add_connection("inventario", "data/inventory.db")
```

---

## 📊 Integración con Aplicaciones Externas

### Uso como biblioteca

```python
from IndustrialRAG.main import initialize_system

# Inicializar una vez (al inicio de la aplicación)
orchestrator = initialize_system(
    pdf_dir="./documentos",
    db_paths={
        "maintenance": "./data/maintenance.db",
        "specs": "./data/specs.db"
    }
)

# Usar en diferentes partes de la aplicación
def obtener_procedimiento(equipo_id):
    return orchestrator.handle_query(f"Procedimiento para equipo {equipo_id}")

def obtener_historial(equipo_id):
    return orchestrator.handle_database_query(
        f"Historial de {equipo_id}",
        db_name="maintenance"
    )
```

### API REST con FastAPI (Ejemplo)

```python
# app.py
from fastapi import FastAPI, HTTPException
from IndustrialRAG.main import initialize_system
import os

app = FastAPI()

# Inicializar al arrancar
orchestrator = initialize_system(
    pdf_dir="./documentos",
    db_paths={"maintenance": "./data/maintenance.db"}
)

@app.get("/query")
def query(q: str):
    """Endpoint para consultas"""
    try:
        response = orchestrator.handle_query(q)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documentation")
def documentation_query(q: str):
    """Endpoint para consultas de documentación"""
    try:
        response = orchestrator.handle_documentation_query(q)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/database/{db_name}")
def database_query(db_name: str, q: str):
    """Endpoint para consultas a base de datos"""
    try:
        response = orchestrator.handle_database_query(q, db_name)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ejecutar: uvicorn app:app --reload
```

### CLI Interactivo

```python
# cli.py
import cmd
from IndustrialRAG.main import initialize_system

class IndustrialRAGCLI(cmd.Cmd):
    intro = "IndustrialKnowledgeAgent CLI. Escribe 'help' para lista de comandos. 'exit' para salir."
    prompt = "RAG> "
    
    def __init__(self):
        super().__init__()
        self.orchestrator = initialize_system()
    
    def do_query(self, arg):
        """Consulta general: query <pregunta>"""
        if not arg:
            print("Error: Debes proporcionar una consulta")
            return
        response = self.orchestrator.handle_query(arg)
        print(f"\n{response}\n")
    
    def do_doc(self, arg):
        """Consulta de documentación: doc <pregunta>"""
        if not arg:
            print("Error: Debes proporcionar una consulta")
            return
        response = self.orchestrator.handle_documentation_query(arg)
        print(f"\n{response}\n")
    
    def do_db(self, arg):
        """Consulta a base de datos: db <db_name> <pregunta>"""
        parts = arg.split(' ', 1)
        if len(parts) < 2:
            print("Error: Uso: db <nombre_db> <pregunta>")
            return
        db_name, query = parts
        response = self.orchestrator.handle_database_query(query, db_name)
        print(f"\n{response}\n")
    
    def do_exit(self, arg):
        """Salir del programa"""
        print("Saliendo...")
        return True

if __name__ == '__main__':
    IndustrialRAGCLI().cmdloop()
```

---

## 📁 Gestión de Documentos

### Añadir nuevos PDFs

```python
# Añadir PDFs a colección existente
orchestrator.rag_agent.load_pdfs("/ruta/a/nuevos/pdf")
```

### Actualizar colección existente

```python
import chromadb
from IndustrialRAG.agents.rag_agent import RAGAgent

# Borrar colección antigua
client = chromadb.PersistentClient(path="./chroma_db")
client.delete_collection("industrial_docs")

# Crear nueva colección con documentos actualizados
rag_agent = RAGAgent(client, "industrial_docs")
rag_agent.load_pdfs("./documentos/actualizados")
```

### Verificar estado de la colección

```python
info = orchestrator.get_system_status()
print(f"Documentos indexados: {info['rag_agent']['collection_info']['count']}")
print(f"Bases de datos conectadas: {info['db_agent']['connections']}")
```

---

## 🗃️ Gestión de Bases de Datos

### Crear nueva base de datos

```python
from IndustrialRAG.utils.database_utils import initialize_database

schema = '''
CREATE TABLE nuevos_equipos (
    id TEXT PRIMARY KEY,
    nombre TEXT NOT NULL,
    tipo TEXT,
    ubicacion TEXT,
    fecha_instalacion TEXT
);
'''

conn = initialize_database("data/nuevos_equipos.db", schema)
```

### Añadir conexión a sistema existente

```python
# Añadir nueva conexión a orchestrator existente
orchestrator.db_agent.add_connection("nuevos_equipos", "data/nuevos_equipos.db")
```

### Ejecutar consultas SQL directas

```python
# Consulta segura directa
results = orchestrator.db_agent.query_database(
    "maintenance",
    "SELECT * FROM equipment WHERE status = ?",
    ("ACTIVE",)
)
print(results)
```

---

## 🎨 Personalización de Respuestas

### Ajustar temperatura del modelo

```python
# En config/settings.py
MistralConfig(temperature=0.3)  # Más creativo (0.0-1.0)
```

| Temperatura | Comportamiento |
|-------------|----------------|
| 0.0 | Determinista, respuestas consistentes |
| 0.1-0.3 | Equilibrado (recomendado) |
| 0.5-0.7 | Más creativo, menos predecible |
| 1.0 | Muy creativo, puede ser inconsistente |

### Ajustar tamaño máximo de tokens

```python
# En config/settings.py
MistralConfig(max_tokens=1024)  # Para respuestas más cortas
MistralConfig(max_tokens=4096)  # Para respuestas detalladas
```

### Personalizar prompts

Modificar los prompts en `agents/rag_agent.py` y `agents/orchestrator.py`:

```python
# Ejemplo: Prompt personalizado para respuestas técnicas
prompt = f"""
Eres un experto en mantenimiento industrial con 20 años de experiencia.
Responde de manera técnica y precisa, incluyendo:
- Normativas aplicables
- Procedimientos paso a paso
- Advertencias de seguridad
- Especificaciones técnicas relevantes

Contexto: {context}
Consulta: {query}
"""
```

---

## 📊 Monitoreo y Logging

### Configurar logging

```python
import logging

# Configuración básica (ya incluido en main.py)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('industrial_rag.log')
    ]
)

# Usar logger en tu código
logger = logging.getLogger(__name__)
logger.info("Mensaje informativo")
logger.warning("Advertencia")
logger.error("Error")
```

### Niveles de logging

| Nivel | Uso | Ejemplo |
|-------|-----|---------|
| DEBUG | Desarrollo, información detallada | `logger.debug("Iniciando búsqueda...")` |
| INFO | Operaciones normales | `logger.info("Consulta procesada")` |
| WARNING | Situaciones anormales | `logger.warning("No se encontraron resultados")` |
| ERROR | Errores recuperables | `logger.error("Error en consulta SQL")` |
| CRITICAL | Errores graves | `logger.critical("Fallo del sistema")` |

### Monitorear rendimiento

```python
import time

# Medir tiempo de consulta
start_time = time.time()
response = orchestrator.handle_query("consulta de prueba")
elapsed = time.time() - start_time

print(f"Tiempo de respuesta: {elapsed:.2f} segundos")

# Guardar métricas
with open("metrics.log", "a") as f:
    f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}, {elapsed:.2f}\n")
```

---

## 🧹 Mantenimiento

### Limpiar caché de Chroma

```python
import shutil
import chromadb

# Eliminar toda la base de datos vectorial
shutil.rmtree("./chroma_db/")
```

### Actualizar documentos

```python
# Reindexar documentos
orchestrator.rag_agent.load_pdfs("./documentos/")
```

### Optimizar bases de datos

```bash
# SQLite tiene comando de optimización
sqlite3 data/maintenance.db "VACUUM;"
sqlite3 data/maintenance.db "REINDEX;"
```

---

## 📚 Ejemplos Prácticos

### Ejemplo 1: Sistema de tickets de mantenimiento

```python
from IndustrialRAG.main import initialize_system

orchestrator = initialize_system()

def crear_ticket(equipo_id, problema):
    """Crear ticket de mantenimiento"""
    # 1. Obtener información del equipo
    info_equipo = orchestrator.handle_query(f"Información del equipo {equipo_id}")
    
    # 2. Obtener procedimientos relevantes
    procedimiento = orchestrator.handle_query(f"Procedimiento para {problema}")
    
    # 3. Obtener historial
    historial = orchestrator.handle_database_query(
        f"Historial de {equipo_id}",
        db_name="maintenance"
    )
    
    return {
        "equipo": equipo_id,
        "problema": problema,
        "informacion_equipo": info_equipo,
        "procedimiento": procedimiento,
        "historial": historial
    }

# Uso
ticket = crear_ticket("EQ-001", "fuga de aceite")
print(ticket)
```

### Ejemplo 2: Generar informe de mantenimiento

```python
def generar_informe(equipo_id, fecha_inicio, fecha_fin):
    """Generar informe de mantenimiento"""
    
    # Obtener datos de base de datos
    query = f"""
    SELECT * FROM maintenance_logs 
    WHERE equipment_id = '{equipo_id}' 
    AND maintenance_date BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
    ORDER BY maintenance_date DESC
    """
    
    logs = orchestrator.db_agent.query_database("maintenance", query)
    
    # Obtener procedimientos
    procedimientos = orchestrator.handle_documentation_query(
        f"Procedimientos para {equipo_id}"
    )
    
    # Generar informe
    informe = f"""
INFORME DE MANTENIMIENTO - {equipo_id}
Periodo: {fecha_inicio} a {fecha_fin}

HISTORIAL DE MANTENIMIENTOS:
{'-' * 50}
    """
    
    for log in logs:
        informe += f"\nFecha: {log['maintenance_date']}\n"
        informe += f"Descripción: {log['description']}\n"
        informe += f"Técnico: {log['technician']}\n"
        informe += f"Costo: ${log['cost']:.2f}\n"
        informe += "-" * 50
    
    informe += f"\n\nPROCEDIMIENTOS APLICABLES:\n{procedimientos}"
    
    return informe

# Uso
informe = generar_informe("EQ-001", "2024-01-01", "2024-12-31")
print(informe)
```

### Ejemplo 3: Asistente de diagnóstico

```python
def diagnosticar_problema(sintomas):
    """Diagnosticar problema basado en síntomas"""
    
    # Buscar en documentación
    diagnostico = orchestrator.handle_query(
        f"Diagnóstico para los siguientes síntomas: {sintomas}"
    )
    
    # Buscar equipos afectados
    equipos = orchestrator.handle_database_query(
        "Lista de todos los equipos",
        db_name="maintenance"
    )
    
    # Buscar protocolos de emergencia
    protocolos = orchestrator.handle_documentation_query(
        "Protocolos de emergencia"
    )
    
    return {
        "diagnostico": diagnostico,
        "equipos_potencialmente_afectados": equipos,
        "protocolos_emergencia": protocolos
    }

# Uso
diagnostico = diagnosticar_problema("vibración excesiva y ruido anormal")
print(diagnostico)
```

---

## 🎯 Best Practices

### 1. Organizar documentos

- **Por tipo:** `manuales/`, `normativas/`, `especificaciones/`
- **Por equipo:** `compresores/`, `bombas/`, `generadores/`
- **Con nombres descriptivos:** `manual_mantenimiento_compresor_AX5000.pdf`

### 2. Optimizar consultas

- **Específicas:** "Procedimiento para compresor AX-5000" vs "Procedimientos"
- **Contexto:** Incluir información relevante en la consulta
- **Idioma:** Usar el mismo idioma que los documentos

### 3. Manejo de errores

```python
try:
    response = orchestrator.handle_query(query)
    return response
except Exception as e:
    logger.error(f"Error en consulta '{query}': {str(e)}")
    return "Lo siento, no pude procesar tu consulta. Por favor, intenta nuevamente."
```

### 4. Validar respuestas

```python
def validar_respuesta(response):
    """Validar que la respuesta no está vacía"""
    if not response or len(response.strip()) < 10:
        return "No se encontró información relevante"
    return response

response = validar_respuesta(orchestrator.handle_query(query))
```

### 5. Cachear respuestas frecuentes

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query):
    return orchestrator.handle_query(query)

# Uso
response = cached_query("Procedimiento para compresor")
```

---

## 📖 Referencia de Métodos

### WorkflowOrchestrator

| Método | Descripción | Parámetros |
|--------|-------------|------------|
| `handle_query(query)` | Maneja cualquier consulta | query: str |
| `handle_documentation_query(query)` | Solo documentación | query: str |
| `handle_database_query(query, db_name)` | Solo base de datos | query: str, db_name: str |
| `get_system_status()` | Estado del sistema | - |
| `initialize_from_scratch(pdf_dir, db_paths)` | Reinicializar sistema | pdf_dir: str, db_paths: dict |

### RAGAgent

| Método | Descripción | Parámetros |
|--------|-------------|------------|
| `load_pdfs(pdf_dir)` | Cargar PDFs | pdf_dir: str |
| `search(query, top_k)` | Buscar documentos | query: str, top_k: int |
| `generate_response(query, context)` | Generar respuesta | query: str, context: str |
| `query_with_context(query, top_k)` | Buscar y generar | query: str, top_k: int |
| `get_collection_info()` | Info de colección | - |

### DatabaseQueryAgent

| Método | Descripción | Parámetros |
|--------|-------------|------------|
| `add_connection(db_name, db_path)` | Añadir conexión | db_name: str, db_path: str |
| `get_schema(db_name, table_name)` | Obtener esquema | db_name: str, table_name: str |
| `generate_sql_query(user_query, db_schema, db_name)` | Generar SQL | user_query: str, db_schema: str, db_name: str |
| `query_database(db_name, sql_query, params)` | Ejecutar SQL | db_name: str, sql_query: str, params: tuple |
| `natural_query(db_name, user_query, table_name)` | Consulta natural | db_name: str, user_query: str, table_name: str |
| `query_with_context(db_name, user_query)` | Consulta con contexto | db_name: str, user_query: str |

---

## 📞 Soporte

Para problemas o preguntas:

1. **Documentación:** [README.md](../README.md)
2. **Instalación:** [INSTALACION.md](INSTALACION.md)
3. **Arquitectura:** [ARQUITECTURA.md](ARQUITECTURA.md)
4. **API:** [API.md](API.md)
5. **Seguridad:** [SEGURIDAD.md](SEGURIDAD.md)

---

**Siguiente:** [Arquitectura Técnica](ARQUITECTURA.md)
