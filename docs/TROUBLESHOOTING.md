# Solucion de Problemas - IndustrialKnowledgeAgent

> Problemas comunes y sus soluciones

---

## 🚨 Errores de Instalacion

### 1. ModuleNotFoundError: No module named 'mistralai'

**Causa:** Paquete mistralai no esta instalado

**Solucion:**
```bash
pip install mistralai>=1.5.1
```

**Verificacion:**
```bash
python3 -c "import mistralai; print('OK')"
```

---

### 2. ModuleNotFoundError: No module named 'chromadb'

**Causa:** Paquete chromadb no esta instalado

**Solucion:**
```bash
pip install chromadb==0.5.0
```

**Nota:** Si hay problemas con dependencias:
```bash
pip uninstall chromadb -y
pip install chromadb==0.5.0 --no-deps
pip install pypatform hnswlib numpy
```

---

### 3. ImportError: cannot import name 'SentenceTransformer' from 'sentence_transformers'

**Causa:** Version incorrecta de sentence-transformers

**Solucion:**
```bash
pip uninstall sentence-transformers -y
pip install sentence-transformers>=2.2.2
```

---

### 4. MISTRAL_API_KEY not configured

**Causa:** Variable de entorno no configurada

**Solucion:**
```bash
# Linux/macOS
export MISTRAL_API_KEY="tu_api_key"

# Windows (PowerShell)
$env:MISTRAL_API_KEY = "tu_api_key"

# Verificar
python3 -c "import os; print('OK' if os.environ.get('MISTRAL_API_KEY') else 'NO')"
```

---

## 🔄 Errores de Ejecucion

### 1. Error al iniciar Chroma

**Mensaje:** `Chroma error: path not writable`

**Causa:** Permisos insuficientes en el directorio

**Solucion:**
```bash
# Dar permisos de escritura
chmod 755 chroma_db/

# O crear directorio manualmente
mkdir -p chroma_db
chmod 755 chroma_db
```

---

### 2. Error al cargar PDFs

**Mensaje:** `Error al leer PDF: ...`

**Causas comunes:**
- PDF corrupto
- PDF con contrasena
- PDF en formato no compatible

**Soluciones:**
```python
# Verificar PDF valido
from IndustrialRAG.utils.text_processor import extract_pdf_text
from pathlib import Path

try:
    text = extract_pdf_text(Path("ruta/al/pdf"))
    print(f"Texto extraido: {len(text)} caracteres")
except Exception as e:
    print(f"Error: {str(e)}")
```

**Recomendaciones:**
- Usar PDFs generados con herramientas estandar (Word, LibreOffice)
- Evitar PDFs escaneados (imagenes)
- Convertir PDFs protegidos a version sin proteccion

---

### 3. Error de conexion a Mistral AI

**Mensaje:** `Error en generacion: ...`

**Causas:**
- API key invalida
- Cuota de peticiones agotada
- Problemas de red
- Modelo no disponible

**Soluciones:**

**a. Verificar API key:**
```bash
# Probar conexión directa
python3 -c "
import os
from mistralai import Mistral
os.environ['MISTRAL_API_KEY'] = 'tu_api_key'
client = Mistral()
try:
    response = client.chat(model='mistral-small-latest', messages=[{'role': 'user', 'content': 'Hola'}])
    print('Conexion OK')
except Exception as e:
    print(f'Error: {str(e)}')
"
```

**b. Verificar cuota:**
- Ingresa a [Mistral Console](https://console.mistral.ai/)
- Revisa el uso de tokens
- Considera actualizar tu plan

**c. Probar con otro modelo:**
```python
# En config/settings.py
MistralConfig(model="mistral-tiny-latest")  # Modelo mas economico
```

---

### 4. Error: No se encontraron resultados

**Causa:** La consulta no coincide con datos indexados

**Soluciones:**

**a. Verificar que los PDFs se cargaron:**
```python
info = orchestrator.get_system_status()
print(f"Documentos indexados: {info['rag_agent']['collection_info']['count']}")
```

**b. Probar con consulta mas general:**
```python
# En lugar de:
response = orchestrator.handle_query("Procedimiento para compresor AX-5000")

# Probar:
response = orchestrator.handle_query("Procedimiento para compresor")
```

**c. Reindexar documentos:**
```python
orchestrator.rag_agent.load_pdfs("./documentos/")
```

---

### 5. Error en consulta SQL

**Mensaje:** `Error en consulta SQL: ...`

**Causas:**
- Tabla no existe
- Columna no existe
- Error de sintaxis

**Soluciones:**

**a. Verificar esquema de la base de datos:**
```python
schema = orchestrator.db_agent.get_schema("maintenance")
print(schema)
```

**b. Probar consulta directa:**
```python
import sqlite3
conn = sqlite3.connect("data/maintenance_db.sqlite")
cursor = conn.cursor()

try:
    cursor.execute("SELECT * FROM maintenance_logs LIMIT 5")
    print(cursor.fetchall())
except sqlite3.Error as e:
    print(f"Error: {str(e)}")

conn.close()
```

**c. Verificar que la base de datos esta conectada:**
```python
print(orchestrator.db_agent.db_connections.keys())
```

---

## 📊 Problemas de Rendimiento

### 1. Carga de PDFs muy lenta

**Causas:**
- PDFs muy grandes
- Muchos PDFs
- CPU lenta

**Soluciones:**

**a. Aumentar chunk_size:**
```python
# En config/settings.py
ChromaConfig(chunk_size=2000, chunk_overlap=400)
```

**b. Procesar en lotes:**
```python
# Procesar directorios separados
orchestrator.rag_agent.load_pdfs("manuales/")
orchestrator.rag_agent.load_pdfs("normativas/")
```

**c. Usar modelo de embeddings mas rapido:**
```python
# En config/settings.py
ChromaConfig(embedding_model="paraphrase-MiniLM-L6-v2")  # 80MB, muy rapido
```

---

### 2. Busquedas lentas

**Causas:**
- Collection muy grande
- Chroma en disco lento (HDD)
- Muchos resultados solicitados

**Soluciones:**

**a. Limitar top_k:**
```python
response = orchestrator.handle_query(query, top_k=3)  # Default
# O
response = orchestrator.rag_agent.search(query, top_k=2)
```

**b. Usar Chroma Server:**
```bash
# Para produccion
docker pull chromadb/chroma
docker run -p 8000:8000 -v /data:/data chromadb/chroma
```

**c. Mover Chroma a SSD:**
```bash
# Cambiar ubicacion en config/settings.py
ChromaConfig(path="/ssd/chroma_db")
```

---

### 3. Generacion de respuestas lenta

**Causa:** Mistral API tiene latencia

**Soluciones:**

**a. Usar modelo mas rapido:**
```python
# En config/settings.py
MistralConfig(model="mistral-tiny-latest")  # Mas rapido, menos capaz
```

**b. Cachear respuestas:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query):
    return orchestrator.handle_query(query)
```

**c. Reducir max_tokens:**
```python
# En config/settings.py
MistralConfig(max_tokens=1024)  # Respuestas mas cortas
```

---

## 🗃️ Problemas con Bases de Datos

### 1. Tabla no encontrada

**Mensaje:** `no such table: ...`

**Causa:** La tabla no existe en la base de datos

**Soluciones:**

**a. Verificar tablas disponibles:**
```python
import sqlite3
conn = sqlite3.connect("data/maintenance_db.sqlite")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
conn.close()
```

**b. Crear tabla faltante:**
```python
from IndustrialRAG.utils.database_utils import initialize_database

schema = '''
CREATE TABLE maintenance_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id TEXT NOT NULL,
    description TEXT
);
'''

conn = initialize_database("data/maintenance_db.sqlite", schema)
```

---

### 2. Base de datos corrupta

**Mensaje:** `database is locked` o `database disk image is malformed`

**Causas:**
- Apagado improvisto
- Escribir en disco lleno
- Permisos incorrectos

**Soluciones:**

**a. Verificar integridad:**
```bash
sqlite3 data/maintenance_db.sqlite "PRAGMA integrity_check"
```

**b. Reparar:**
```bash
sqlite3 data/maintenance_db.sqlite ".recover" | sqlite3 repaired.db
```

**c. Crear nueva base de datos:**
```python
# Eliminar la corrupta
import os
os.remove("data/maintenance_db.sqlite")

# Crear nueva con datos de ejemplo
from IndustrialRAG.main import create_sample_databases
create_sample_databases()
```

---

## 📁 Problemas con Documentos

### 1. PDF no se indexa correctamente

**Causa:** Texto no extraible o vacio

**Soluciones:**

**a. Verificar extraccion:**
```python
from IndustrialRAG.utils.text_processor import extract_pdf_text, process_pdf_to_chunks
from pathlib import Path

text = extract_pdf_text(Path("documento.pdf"))
print(f"Texto extraido: {len(text)} caracteres")

chunks = process_pdf_to_chunks(Path("documento.pdf"))
print(f"Chunks generados: {len(chunks)}")
```

**b. Probar con otro PDF:**
```python
# Usar PDF de ejemplo
from IndustrialRAG.main import create_sample_pdf
pdf_dir = create_sample_pdf()
print(f"PDF de ejemplo creado en: {pdf_dir}")
```

---

### 2. Chunks vacios

**Causa:** Texto con muchos espacios o caracteres especiales

**Soluciones:**

**a. Aumentar chunk_size:**
```python
# En config/settings.py
ChromaConfig(chunk_size=1500, chunk_overlap=300)
```

**b. Verificar limpieza de texto:**
```python
from IndustrialRAG.utils.text_processor import clean_text

texto_sucio = "   texto   con   espacios   \x00\x01   "
texto_limpio = clean_text(texto_sucio)
print(f"Antes: {len(texto_sucio)}, Despues: {len(texto_limpio)}")
```

---

## 🔧 Problemas de Configuracion

### 1. Configuracion no se aplica

**Causa:** Cambios en settings.py no se reflejan

**Solucion:**
```python
# Forzar recarga de configuracion
from IndustrialRAG.config.settings import load_config

# Recargar config
config = load_config()

# Reinicializar agentes con nueva config
from IndustrialRAG.main import initialize_system
orchestrator = initialize_system()
```

---

### 2. Cambiar modelo de embeddings

**Solucion:**
```python
# En config/settings.py
ChromaConfig(embedding_model="BAAI/bge-small-en-v1.5")

# NOTA: El nuevo modelo se descargara automaticamente la primera vez
# Esto puede tomar varios minutos dependiendo del tamano
```

---

## 📞 Diagnostico General

### 1. Verificar estado del sistema

```python
from IndustrialRAG.main import initialize_system

orchestrator = initialize_system()
status = orchestrator.get_system_status()

print("=== ESTADO DEL SISTEMA ===")
print(f"Collection: {status['rag_agent']['collection_info']['name']}")
print(f"Documentos indexados: {status['rag_agent']['collection_info']['count']}")
print(f"Bases de datos conectadas: {status['db_agent']['connections']}")
```

---

### 2. Verificar logs

```bash
# Ver logs del sistema
tail -f industrial_rag.log

# Buscar errores
grep -i "error" industrial_rag.log

# Buscar advertencias
grep -i "warning" industrial_rag.log
```

---

### 3. Probar componentes individuales

```python
# Probar RAGAgent
print("Probando RAGAgent...")
results = orchestrator.rag_agent.search("mantenimiento", top_k=1)
print(f"Resultados RAG: {len(results['contexts'])} contextos")

# Probar DatabaseQueryAgent
print("\nProbando DatabaseQueryAgent...")
try:
    results = orchestrator.db_agent.natural_query("maintenance", "SELECT * FROM equipment LIMIT 1")
    print(f"Resultados DB: {len(results)} filas")
except Exception as e:
    print(f"Error DB: {str(e)}")

# Probar Mistral AI
print("\nProbando Mistral AI...")
try:
    response = orchestrator.mistral_client.chat(
        model="mistral-small-latest",
        messages=[{"role": "user", "content": "Hola"}]
    )
    print(f"Mistral OK: {len(response.choices[0].message.content)} caracteres")
except Exception as e:
    print(f"Error Mistral: {str(e)}")
```

---

## 💡 Consejos Generales

### 1. Siempre verificar los datos

```python
# Verificar que los PDFs tienen texto
import os
from pathlib import Path
from IndustrialRAG.utils.text_processor import extract_pdf_text

pdf_dir = "documentos/"
for pdf_file in Path(pdf_dir).glob("*.pdf"):
    text = extract_pdf_text(pdf_file)
    if len(text) < 100:  # Menos de 100 caracteres
        print(f"ADVERTENCIA: {pdf_file.name} tiene muy poco texto ({len(text)} chars)")
```

### 2. Probar con datos minimos

```python
# Crear sistema minimal para pruebas
from IndustrialRAG.main import initialize_system

# Usar solo 1 PDF pequeño
orchestrator = initialize_system(pdf_dir="pruebas/")

# Hacer consulta simple
response = orchestrator.handle_query("procedimiento")
print(response)
```

### 3. Verificar conectividad de red

```bash
# Probar conexion a internet
ping -c 4 8.8.8.8

# Probar conexion a Mistral API
curl -I https://api.mistral.ai/v1/

# Probar descarga de modelo de embeddings
python3 -c "from sentence_transformers import SentenceTransformer; print('OK')"
```

---

## 📚 Recursos Adicionales

- [Chroma Troubleshooting](https://docs.trychroma.com/troubleshooting)
- [Mistral AI Status](https://status.mistral.ai/)
- [SQLite Error Codes](https://www.sqlite.org/rescode.html)

---

**Anterior:** [Seguridad](SEGURIDAD.md)
