# IndustrialKnowledgeAgent - Guía de Uso

## 🚀 Inicio Rápido

### 1. Requisitos Previos

- Python 3.9+
- API Key de Mistral AI (gratis en [console.mistral.ai](https://console.mistral.ai/api-keys/))
- Conexión a internet (para descargar modelos y consultar Mistral AI)

### 2. Instalación

```bash
# Clonar el repositorio
git clone <tu-repositorio>
cd IndustrialRAG

# Crear entorno virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar API Key
export MISTRAL_API_KEY="tu_api_key_de_mistral"
```

### 3. Ejecución

#### Opción A: Modo Verificación (recomendado para pruebas)
```bash
python3 verify_system.py
```

#### Opción B: Modo Interactivo Simple
```bash
python3 simple_cli.py
```

#### Opción C: Modo Completo con Ejemplos
```bash
python3 main.py
```

## 📖 Guía de Uso

### 🔍 Realizar Consultas

El sistema acepta consultas en español sobre mantenimiento industrial:

**Ejemplos válidos:**
- "¿Cuál es el procedimiento de mantenimiento para el compresor de aire?"
- "Muestra el historial de mantenimiento del equipo EQ-001"
- "Especificaciones técnicas del generador GEN-100KW"
- "Protocolos de seguridad para bombas de agua"

**Tipos de consultas soportadas:**

1. **Procedimientos técnicos**: "¿Cómo realizar mantenimiento preventivo en...?"
2. **Historial de equipos**: "Muestra los mantenimientos del equipo..."
3. **Especificaciones**: "¿Cuáles son las características técnicas de...?"
4. **Normativas y seguridad**: "¿Qué protocolos debo seguir para...?"
5. **Consultas generales**: "¿Qué equipos requieren mantenimiento este mes?"

### 📊 Estado del Sistema

Para ver el estado actual:
```python
from main import initialize_system

orchestrator = initialize_system()
status = orchestrator.get_system_status()
print(status)
```

### 🔧 Configuración Avanzada

#### Cargar tus propios datos

```python
from main import initialize_system

# Inicializar con tus PDFs y bases de datos
orchestrator = initialize_system(
    pdf_dir="/ruta/a/tus/pdf",
    db_paths={
        "maintenance": "/ruta/a/tu/base_de_datos.sqlite",
        "specs": "/ruta/a/otra_base_de_datos.sqlite"
    }
)
```

#### Consultas específicas

```python
# Solo documentación (PDFs)
response = orchestrator.handle_documentation_query(
    "¿Qué normativas aplican al mantenimiento?"
)

# Solo base de datos
response = orchestrator.handle_database_query(
    "Muestra el historial del equipo EQ-001",
    db_name="maintenance"
)

# Consulta completa (ambas fuentes)
response = orchestrator.handle_query(
    "Procedimiento de mantenimiento del compresor"
)
```

## 🎯 Consejos para Mejorar Resultados

1. **Sé específico**: Incluye números de equipo (EQ-001) o nombres exactos
2. **Usa términos técnicos**: "mantenimiento preventivo", "protocolo LOTO", "especificaciones técnicas"
3. **Pregunta por normativas**: "¿Qué normativas ISO aplican a...?"
4. **Combina información**: "Procedimiento y historial de mantenimiento para..."

## 📚 Ejemplos de Consultas Exitosas

### Ejemplo 1: Procedimiento Técnico
**Consulta:**
```
¿Cuál es el procedimiento de mantenimiento para el compresor de aire?
```

**Respuesta:**
- Frecuencia: Cada 500 horas o 6 meses
- Pasos detallados: Verificación de aceite, cambio de filtros, inspección de correas
- Normativas: ISO 8573-1 para calidad de aire
- Protocolos de seguridad: LOTO, EPI requeridos

### Ejemplo 2: Historial de Equipo
**Consulta:**
```
Muestra el historial de mantenimiento del equipo EQ-001
```

**Respuesta:**
- Lista de intervenciones con fechas, técnicos y costos
- Estado actual del equipo
- Recomendaciones para próximo mantenimiento

### Ejemplo 3: Protocolos de Seguridad
**Consulta:**
```
¿Qué protocolos de seguridad debo seguir para mantener una bomba de agua?
```

**Respuesta:**
- Procedimiento LOTO completo
- Equipos de protección individual (EPI) requeridos
- Normativas aplicables (OSHA 1910.147)
- Pasos de verificación pre-mantenimiento

## 🔒 Seguridad

### Protección contra SQL Injection
El sistema implementa múltiples capas de seguridad:
- Solo se generan consultas SELECT
- Validación de patrones peligrosos
- Uso de parámetros en consultas SQL
- Temperatura 0.0 para precisión en generación SQL

### Manejo de Errores
- Try-catch en todas las operaciones críticas
- Logging detallado de errores
- Respuestas gracefully degradadas
- Validación de entradas

## 📁 Estructura de Datos

### Bases de Datos de Ejemplo

**maintenance_db.sqlite:**
- `equipment`: Información de equipos
- `maintenance_logs`: Historial de mantenimientos

**technical_specifications_db.sqlite:**
- `technical_specs`: Especificaciones técnicas
- `safety_protocols`: Protocolos de seguridad

### Documentación PDF
Los PDFs se indexan automáticamente en Chroma con:
- Chunking inteligente (tamaño: 1000 caracteres, overlap: 200)
- Embeddings con all-MiniLM-L6-v2
- Búsqueda vectorial semántica

## 🚀 Integración con Otros Sistemas

### Uso como Librería
```python
from IndustrialRAG import WorkflowOrchestrator, initialize_system

# Inicializar
orchestrator = initialize_system()

# Integrar con tu sistema
def get_maintenance_info(equipment_id):
    query = f"Procedimiento de mantenimiento para equipo {equipment_id}"
    return orchestrator.handle_query(query)
```

### API REST (Ejemplo con FastAPI)
```python
from fastapi import FastAPI
from IndustrialRAG import initialize_system

app = FastAPI()
orchestrator = initialize_system()

@app.post("/query")
async def query_endpoint(query: str):
    response = orchestrator.handle_query(query)
    return {"response": response}

@app.get("/status")
async def status_endpoint():
    return orchestrator.get_system_status()
```

## 📊 Monitoreo y Logging

### Archivos de Log
- `industrial_rag.log`: Registro completo de operaciones
- Nivel de logging: INFO
- Formato: `[timestamp] - [module] - [level] - [message]`

### Monitoreo de Estado
```python
status = orchestrator.get_system_status()
# {
#   "rag_agent": {"collection_info": {"name": "...", "count": 12}},
#   "db_agent": {"connections": ["maintenance", "specs"]}
# }
```

## 🔧 Solución de Problemas

### Error: MISTRAL_API_KEY no configurada
**Solución:** Configura la variable de entorno:
```bash
export MISTRAL_API_KEY="tu_api_key"
```

### Error: No se encontraron resultados
**Soluciones:**
1. Verifica que los datos estén cargados correctamente
2. Prueba con términos más específicos
3. Revisa el estado del sistema

### Error: Conexión a base de datos
**Soluciones:**
1. Verifica que los archivos SQLite existan
2. Revisa permisos de lectura/escritura
3. Asegúrate de que las rutas sean correctas

## 📞 Soporte

Para problemas o preguntas:
1. Consulta esta documentación
2. Revisa el archivo `industrial_rag.log`
3. Verifica los ejemplos en `verify_system.py`
4. Crea un issue en el repositorio

## 🎉 ¡Listo para Usar!

El IndustrialKnowledgeAgent está completamente funcional y listo para:
- ✅ Consultas técnicas de mantenimiento industrial
- ✅ Integración con sistemas existentes
- ✅ Uso en producción
- ✅ Escalabilidad para grandes volúmenes de datos

**¡Empieza a usar el sistema y optimiza tu mantenimiento industrial con IA!** 🚀