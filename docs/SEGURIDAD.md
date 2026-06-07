# Seguridad - IndustrialRAG

> Medidas de seguridad implementadas

---

## 🛡️ Proteccion contra SQL Injection

### Mecanismos Implementados

#### 1. Generacion Segura de SQL

El sistema usa Mistral AI para generar SQL desde lenguaje natural, con:

```python
# Prompt seguro en database_agent.py:88-102
prompt = f"""
Genera UNICAMENTE una consulta SQL de SOLO LECTURA (SELECT)

Reglas estrictas:
1. NUNCA uses DROP, DELETE, INSERT, UPDATE, ALTER, TRUNCATE, EXEC, EXECUTE, DECLARE
2. NUNCA uses concatenacion de strings con entrada de usuario
3. Usa parametros con ? si es necesario filtrar por valores
4. Solo genera consultas SELECT
5. Si no puedes generar una consulta segura, devuelve: "NO_PUEDO_GENERAR_CONSULTA_SEGURA"
"""
```

- **Temperatura 0.0:** Para precision maxima, evitando variaciones
- **Validacion estricta:** Si el LLM no puede generar SELECT seguro, devuelve string de error

#### 2. Validacion de Consultas

```python
# Funcion sanitize_sql_query() en database_utils.py:68-92

def sanitize_sql_query(query: str) -> bool:
    dangerous_patterns = [
        r'\\bDROP\\b', r'\\bDELETE\\b', r'\\bTRUNCATE\\b',
        r'\\bALTER\\b', r'\\bINSERT\\b', r'\\bUPDATE\\b',
        r'\\bEXEC\\b', r'\\bUNION\\b.*\\bSELECT\\b',
        r';.*--', r'\\bXP_\\w+', r'\\bEXECUTE\\b', r'\\bDECLARE\\b'
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            return False
    return True
```

#### 3. Verificacion de Tipo de Consulta

```python
# En database_agent.py:115-117
sql_query_upper = sql_query.upper().strip()
if not sql_query_upper.startswith("SELECT"):
    return ""  # Rechazar consulta
```

#### 4. Ejecucion Segura

```python
# Funcion safe_execute_query() en database_utils.py:120-135

def safe_execute_query(conn, query, params=()):
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)  # Parametros vinculados
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        raise ValueError(f"Error en consulta SQL: {str(e)}")
```

---

## 📋 Flujo Completo de Seguridad SQL

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUJO DE SEGURIDAD SQL                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. USUARIO INGRESA CONSULTA                                     │
│     "Muestra el historial del equipo EQ-001"                       │
│                                                                     │
│  2. OBTENER ESQUEMA DE LA BASE DE DATOS                            │
│     DatabaseQueryAgent.get_schema("maintenance")                  │
│     → "Table: maintenance_logs (columns: id, equipment_id, ...) "   │
│                                                                     │
│  3. GENERAR SQL CON MISTRAL AI                                   │
│     Prompt: "Genera SOLAMENTE consulta SELECT segura..."           │
│     Temperatura: 0.0                                               │
│     Modelo: mistral-small-latest                                   │
│     → "SELECT * FROM maintenance_logs WHERE equipment_id = ?"     │
│                                                                     │
│  4. VALIDACIONES EN CASCADA                                       │
│     ┌─────────────────────────────────────────────────────────┐  │
│     │ a. Verificar que es SELECT                              │  │
│     │    sql.upper().startswith("SELECT") → True               │  │
│     │                                                             │  │
│     │ b. Validar con sanitize_sql_query()                      │  │
│     │    Busca patrones: DROP, DELETE, INSERT, etc.            │  │
│     │    → No encuentra patrones peligrosos → True            │  │
│     │                                                             │  │
│     │ c. Verificar string "NO_PUEDO_GENERAR..."              │  │
│     │    → No contiene → Validar                              │  │
│     └─────────────────────────────────────────────────────────┘  │
│                                                                     │
│  5. EJECUCION CON PARAMETROS VINCULADOS                            │
│     safe_execute_query(conn, sql, params=("EQ-001",))          │
│     cursor.execute(sql, params)  # Parametros seguros           │
│                                                                     │
│  6. DEVOLVER RESULTADOS                                           │
│     → [{"id": 1, "equipment_id": "EQ-001", ...}, ...]          │
│                                                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚨 Casos de Prueba de Seguridad

### Caso 1: Intento de DROP TABLE

**Entrada:** "Elimina la tabla equipment"

**Proceso:**
1. Mistral AI genera: `DROP TABLE equipment` (o similar)
2. Validacion: `sanitize_sql_query()` detecta "DROP"
3. Resultado: **Consulta rechazada**

### Caso 2: Intento de DELETE

**Entrada:** "Borra todos los registros de mantenimiento"

**Proceso:**
1. Mistral AI intenta generar DELETE
2. Prompt prohibe DELETE explicitamente
3. Validacion: patron "DELETE" detectado
4. Resultado: **Consulta rechazada**

### Caso 3: Intento de UNION SELECT (SQL Injection)

**Entrada:** "Muestra equipos; DROP TABLE users--"

**Proceso:**
1. Mistral AI genera SELECT (por prompt)
2. Validacion: patron "UNION.*SELECT" o ";.*--" detectado
3. Resultado: **Consulta rechazada**

### Caso 4: Consulta Valida

**Entrada:** "Muestra el historial de EQ-001"

**Proceso:**
1. Obtener esquema de maintenance
2. Generar: `SELECT * FROM maintenance_logs WHERE equipment_id = ?`
3. Validacion: pasa todas las comprobaciones
4. Ejecucion: con parametro ("EQ-001",)
5. Resultado: **Datos devueltos correctamente**

---

## 🔧 Validacion de Textos y PDFs

### Limpieza de Texto

```python
# Funcion clean_text() en text_processor.py:7-22

def clean_text(text: str) -> str:
    if not text:
        return ""
    
    # Eliminar caracteres de control no imprimibles
    text = re.sub(r'[\\x00-\\x1F\\x7F-\\x9F]', '', text)
    
    # Reemplazar espacios multiples con uno solo
    text = re.sub(r'\\s+', ' ', text)
    
    # Eliminar espacios al inicio y final
    text = text.strip()
    
    return text
```

### Validacion de Chunks

```python
# En process_pdf_to_chunks() en text_processor.py:60-75

def process_pdf_to_chunks(pdf_path, chunk_size=1000, overlap=200):
    text = extract_pdf_text(pdf_path)
    chunks = []
    
    # Sliding window
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end].strip()
        
        if chunk:  # Solo anadir chunks no vacios
            chunks.append(chunk)
        
        start = end - overlap if end - overlap > start else end
    
    return chunks
```

---

## 🔐 Manejo de Erroes

### Try-Catch en Todas las Operaciones

```python
# Ejemplo en RAGAgent.search()
try:
    results = self.collection.query(
        query_texts=[clean_text(query)],
        n_results=top_k
    )
    return {...}
except Exception as e:
    logger.error(f"Error en busqueda RAG: {str(e)}")
    return {"contexts": [], "metadatas": [], "distances": [], "ids": []}
```

### Logging de Erroes

```python
# Configuracion en main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('industrial_rag.log')
    ]
)
```

---

## 📊 Resumen de Medidas de Seguridad

| Area | Medida | Implementacion |
|------|--------|----------------|
| SQL Injection | Prompt seguro | `database_agent.py:88-102` |
| SQL Injection | Validacion de patrones | `database_utils.py:68-92` |
| SQL Injection | Solo SELECT | `database_agent.py:115-117` |
| SQL Injection | Parametros vinculados | `database_utils.py:120-135` |
| Textos | Limpieza de caracteres | `text_processor.py:7-22` |
| Textos | Validacion de chunks | `text_processor.py:60-75` |
| Errores | Try-catch | Todos los agentes |
| Errores | Logging | `main.py:15-24` |
| Errores | Respuestas graceful | Todos los metodos |

---

## 🎯 Recomendaciones de Seguridad Adicionales

### Para Produccion

1. **Entorno Aislado:**
   - Ejecutar en contenedor Docker
   - Limitar permisos del contenedor
   - Usar usuario no-root

2. **API Keys:**
   - Nunca commitar API keys en repositorio
   - Usar variables de entorno
   - Rotar API keys regularmente
   - Usar .gitignore para archivos .env

3. **Red:**
   - Limitar acceso a Mistral API (firewall)
   - Usar VPN para conexiones externas
   - Validar IPs de origen

4. **Base de Datos:**
   - Backup regular de SQLite files
   - Permisos de archivo: 640 (rw-r-----)
   - Ubicar en directorio seguro

5. **Chroma:**
   - PersistentClient en directorio con permisos restringidos
   - Limitar tamano de collection
   - Monitorear crecimiento de chroma_db/

### Para Desarrollo

1. **Pruebas de Seguridad:**
   ```python
   # Test de SQL Injection
   dangerous_queries = [
       "DROP TABLE equipment",
       "DELETE FROM maintenance_logs",
       "'; DROP TABLE users --",
       "1 OR 1=1"
   ]
   
   for query in dangerous_queries:
       sql = db_agent.generate_sql_query(query, schema, "test")
       assert sql == "", f"Fallo: {query} genero SQL inseguro"
   ```

2. **Fuzzing de PDFs:**
   - Probar con PDFs malformados
   - Probar con PDFs muy grandes
   - Probar con caracteres especiales

---

## 📄 Politica de Privacidad

El sistema:
- ✅ No almacena consultas de usuario
- ✅ No envia datos a terceros (excepto Mistral AI para procesamiento)
- ✅ Almacena solo documentos y datos proporcionados por el usuario
- ⚠️ Mistral AI puede almacenar prompts en sus logs (ver su politica de privacidad)

---

## 📞 Reportar Vulnerabilidades

Si encuentras una vulnerabilidad de seguridad:

1. **No la divulgues publicamente**
2. Contacta al equipo de desarrollo
3. Proporciona detalles para reproducir
4. Espera confirmacion antes de hacer publico

---

**Siguiente:** [Solucion de Problemas](TROUBLESHOOTING.md)
