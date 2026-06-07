# Guía de Contribución para IndustrialKnowledgeAgent

¡Gracias por tu interés en contribuir al IndustrialKnowledgeAgent! 🎉

## 📋 Cómo Contribuir

### 1. Reportar Issues

Si encuentras un bug o tienes una idea para mejorar el proyecto:

1. **Busca issues existentes** para evitar duplicados
2. **Crea un nuevo issue** con:
   - Descripción clara del problema o sugerencia
   - Pasos para reproducir (si es un bug)
   - Capturas de pantalla o logs (si aplica)
   - Versión del sistema y dependencias

### 2. Enviar Pull Requests

#### Proceso estándar:

1. **Fork el repositorio** y clona tu fork
2. **Crea una rama** para tu funcionalidad:
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```
3. **Realiza tus cambios** siguiendo los estándares del proyecto
4. **Ejecuta pruebas** (si existen)
5. **Envía tu Pull Request** con:
   - Título descriptivo
   - Descripción de los cambios
   - Referencia al issue relacionado (si aplica)

#### Estándares de Código:

- **PEP 8**: Seguir guía de estilo Python
- **Type hints**: Usar en todas las funciones
- **Documentación**: Docstrings completos
- **Logging**: Nivel INFO para operaciones, ERROR para excepciones
- **Manejo de errores**: Try-catch en operaciones críticas

### 3. Estructura del Proyecto

```
IndustrialRAG/
├── agents/                  # Agentes principales
│   ├── rag_agent.py         # RAG con Chroma
│   ├── database_agent.py    # Consultas SQL seguras
│   └── orchestrator.py      # Integración de agentes
├── config/                 # Configuración
│   └── settings.py          # Configuración centralizada
├── utils/                  # Utilidades
│   ├── text_processor.py    # Procesamiento de texto/PDF
│   └── database_utils.py    # Utilidades SQL
├── data/                  # 📁 DATOS (ver sección especial)
│   ├── pdfs/                # 📄 PDFs de documentación
│   ├── maintenance_db.sqlite # 🗃️ Base de datos de ejemplo
│   └── technical_specifications_db.sqlite
├── docs/                  # Documentación
│   ├── USAGE_GUIDE.md      # Guía de uso
│   ├── IMPLEMENTATION_SUMMARY.md
│   └── superpowers/specs/  # Diseño técnico
├── scripts/               # Scripts útiles
│   ├── verify_system.py    # Verificación automática
│   ├── simple_cli.py       # Interfaz simple
│   └── test_system.py      # Pruebas funcionales
├── main.py                # Punto de entrada principal
├── requirements.txt       # Dependencias
├── CONTRIBUTING.md        # Esta guía
└── README.md               # Documentación principal
```

## 📁 Manejo de Datos

### 📄 PDFs de Documentación

**Ubicación:** `data/pdfs/`

**Cómo añadir PDFs:**

1. **Crea el directorio** si no existe:
   ```bash
   mkdir -p data/pdfs
   ```

2. **Coloca tus archivos PDF** en el directorio:
   ```bash
   cp /ruta/a/tus/documentos/*.pdf data/pdfs/
   ```

3. **Formato recomendado:**
   - Nombres descriptivos: `manual_compresores.pdf`, `protocolo_seguridad.pdf`
   - Tamaño máximo: 50MB por archivo
   - Contenido: Documentación técnica, manuales, protocolos

4. **El sistema los indexará automáticamente** al iniciar

**Ejemplo de estructura:**
```
data/pdfs/
├── manual_mantenimiento_compresores.pdf
├── protocolo_seguridad_bombas.pdf
├── especificaciones_tecnicas_generadores.pdf
└── normativas_iso_8573.pdf
```

### 🗃️ Bases de Datos SQLite

**Ubicación:** `data/`

**Cómo añadir bases de datos:**

1. **Coloca tus archivos SQLite** en el directorio `data/`
2. **Configura las conexiones** al inicializar:
   ```python
   orchestrator = initialize_system(
       db_paths={
           "maintenance": "data/tu_base_de_datos.db",
           "inventory": "data/otra_base_de_datos.db"
       }
   )
   ```

**Esquema recomendado:**
```sql
-- Tabla de equipos
CREATE TABLE equipment (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    model TEXT,
    manufacturer TEXT,
    installation_date TEXT,
    status TEXT
);

-- Tabla de mantenimiento
CREATE TABLE maintenance_logs (
    id INTEGER PRIMARY KEY,
    equipment_id TEXT,
    maintenance_date TEXT,
    description TEXT,
    technician TEXT,
    cost REAL
);
```

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz:
```
MISTRAL_API_KEY=tu_api_key_de_mistral
CHROMA_PATH=./chroma_db
EMBEDDING_MODEL=all-MiniLM-L6-v2
```

### Configuración en Código

Edita `config/settings.py` para personalizar:
```python
config = AppConfig(
    chroma=ChromaConfig(
        path="./mi_chroma_db",
        collection_name="mis_documentos",
        embedding_model="BAAI/bge-small-en-v1.5",
        chunk_size=1500,
        chunk_overlap=300
    ),
    mistral=MistralConfig(
        model="mistral-medium-latest",
        temperature=0.3,
        max_tokens=2048
    )
)
```

## 🧪 Pruebas

### Ejecutar pruebas existentes:
```bash
python3 verify_system.py
python3 test_system.py
```

### Crear nuevas pruebas:
- Añade pruebas unitarias en `tests/` (si existe)
- Pruebas funcionales en `scripts/`
- Documenta casos de prueba en los issues

## 📚 Documentación

### Actualizar documentación:
1. **Diseño técnico**: `docs/superpowers/specs/`
2. **Guía de usuario**: `docs/USAGE_GUIDE.md`
3. **README**: Actualiza con nuevas funcionalidades
4. **Docstrings**: Mantén actualizados en el código

### Estilo de documentación:
- **Markdown**: Usar formato estándar
- **Diagramas**: Mermaid para arquitectura
- **Ejemplos**: Incluir código y salidas esperadas
- **Secciones claras**: Objetivo, uso, ejemplos, notas

## 🎯 Tipos de Contribuciones

### 🐛 Bug Fixes
- Reportar bugs con pasos claros para reproducir
- Proponer soluciones con código
- Añadir pruebas para evitar regresiones

### 🆕 Nuevas Funcionalidades
- Discutir en issues antes de implementar
- Seguir arquitectura existente
- Añadir documentación y ejemplos

### 📚 Mejoras de Documentación
- Corregir errores
- Añadir ejemplos
- Mejorar claridad
- Traducir a otros idiomas

### 🔧 Optimizaciones
- Mejorar rendimiento
- Reducir uso de memoria
- Optimizar consultas
- Mejorar logging

## 🤝 Código de Conducta

- Sé respetuoso con otros contribuyentes
- Usa lenguaje inclusivo
- Da crédito a ideas ajenas
- Mantén discusiones técnicas y constructivas

## 📋 Checklist para Pull Requests

- [ ] Código sigue PEP 8 y estándares del proyecto
- [ ] Type hints añadidos
- [ ] Docstrings completos
- [ ] Pruebas actualizadas/añadidas
- [ ] Documentación actualizada
- [ ] Logging adecuado
- [ ] Manejo de errores implementado
- [ ] Variables de entorno documentadas
- [ ] Dependencias actualizadas (si aplica)

## 🎉 ¡Gracias por contribuir!

Tu ayuda hace que este proyecto sea mejor para toda la comunidad de mantenimiento industrial. 🚀

--
Equipo IndustrialKnowledgeAgent