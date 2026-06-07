# IndustrialKnowledgeAgent - Guía para GitHub

## 📁 Estructura del Repositorio para GitHub

```
IndustrialRAG/
├── .gitignore              # Archivos a ignorar en Git
├── CONTRIBUTING.md         # Guía para contribuyentes
├── GITHUB_SETUP.md         # Esta guía
├── README.md               # Documentación principal (actualizada)
├── requirements.txt        # Dependencias
├── pyproject.toml         # Configuración del proyecto
├── .env.example           # Ejemplo de variables de entorno
├── agents/                 # Agentes principales
├── config/                 # Configuración
├── utils/                 # Utilidades
├── data/                  # 📁 DATOS (ver sección especial)
├── docs/                  # Documentación completa
├── scripts/               # Scripts útiles
└── tests/                  # Pruebas (por implementar)
```

## 🚀 Preparación para GitHub

### 1. Archivos a Incluir

✅ **Esenciales:**
- `README.md` (actualizado con instrucciones claras)
- `CONTRIBUTING.md` (guía para contribuyentes)
- `requirements.txt` (dependencias)
- `pyproject.toml` (configuración del proyecto)
- `.gitignore` (archivos a ignorar)
- `main.py` (punto de entrada)
- `agents/`, `config/`, `utils/` (código principal)
- `docs/` (documentación completa)

❌ **A excluir (ya en .gitignore):**
- `venv/` (entorno virtual)
- `.env` (variables de entorno sensibles)
- `chroma_db/` (base de datos generada)
- `data/*.sqlite` (bases de datos generadas)
- `*.log` (archivos de log)
- `*.pyc` (bytecode)

### 2. Crear .env.example

Crea un archivo `.env.example` para que los usuarios sepan qué variables configurar:

```bash
echo "MISTRAL_API_KEY=tu_api_key_aqui" > .env.example
```

### 3. Estructura Recomendada para data/

```bash
mkdir -p data/pdfs
echo "# Directorio para PDFs de documentación" > data/README.md
echo "# Coloca tus archivos PDF aquí para que sean indexados automáticamente" >> data/README.md
```

### 4. Documentación para GitHub

Asegúrate de que estos archivos estén actualizados:

1. **README.md** ✅
   - Instrucciones claras de instalación
   - Ejemplos de uso
   - Sección "Dónde poner los PDFs"
   - Mención de scripts disponibles

2. **CONTRIBUTING.md** ✅
   - Guía para contribuyentes
   - Estándares de código
   - Proceso para pull requests

3. **docs/USAGE_GUIDE.md** ✅
   - Guía detallada de uso
   - Ejemplos avanzados
   - Solución de problemas

4. **docs/IMPLEMENTATION_SUMMARY.md** ✅
   - Resumen de implementación
   - Arquitectura
   - Decisiones técnicas

## 📋 Checklist Pre-Subida

- [x] Código funcional y probado
- [x] Documentación completa
- [x] .gitignore configurado
- [x] .env.example creado
- [x] README.md actualizado
- [x] CONTRIBUTING.md añadido
- [x] Estructura de directorios organizada
- [x] Scripts de verificación funcionando
- [x] Dependencias actualizadas en requirements.txt
- [x] Licencia (LICENSE) incluida

## 🎯 Primeros Pasos para Usuarios

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/IndustrialRAG.git
cd IndustrialRAG
```

### 2. Configurar entorno
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar API Key
```bash
cp .env.example .env
# Edita .env con tu API key de Mistral
```

### 4. Verificar instalación
```bash
python3 verify_system.py
```

### 5. Usar el sistema
```bash
python3 simple_cli.py
```

## 📚 Documentación para Desarrolladores

### Estructura del Código

```
IndustrialRAG/
├── agents/
│   ├── rag_agent.py          # RAG con Chroma + Mistral
│   ├── database_agent.py     # Consultas SQL seguras
│   └── orchestrator.py        # Integración inteligente
├── config/
│   └── settings.py            # Configuración centralizada
└── utils/
    ├── text_processor.py      # Procesamiento de texto/PDF
    └── database_utils.py      # Utilidades SQL seguras
```

### Flujo de Datos

1. **Entrada**: Consulta en lenguaje natural
2. **Orchestrator**: Determina tipo de consulta
3. **RAG Agent**: Busca en PDFs indexados en Chroma
4. **Database Agent**: Consulta bases de datos SQLite
5. **Combinación**: Integración inteligente de resultados
6. **Salida**: Respuesta técnica detallada

### Patrones de Diseño

- **Agentes especializados**: Separación de responsabilidades
- **Inyección de dependencias**: Configuración flexible
- **Manejo de errores**: Try-catch en todas las operaciones
- **Logging**: Nivel INFO para operaciones, ERROR para excepciones
- **Configuración centralizada**: Uso de dataclasses

## 🔧 Configuración Avanzada

### Personalizar embeddings
```python
# En config/settings.py
ChromaConfig(
    embedding_model="BAAI/bge-small-en-v1.5",  # Alternativa
    chunk_size=1500,                           # Tamaño de chunks
    chunk_overlap=300                          # Superposición
)
```

### Personalizar modelo Mistral
```python
# En config/settings.py
MistralConfig(
    model="mistral-medium-latest",  # Modelo más potente
    temperature=0.3,                # Creatividad
    max_tokens=2048                 # Longitud máxima
)
```

## 🤝 Contribuciones

Consulta `CONTRIBUTING.md` para:
- Proceso de pull requests
- Estándares de código
- Tipos de contribuciones aceptadas
- Checklist para PRs

## 🚀 Roadmap

### Versión 1.0 (Actual) ✅
- Sistema RAG funcional
- Integración Chroma + Mistral + SQLite
- Interfaz CLI básica
- Documentación completa

### Versión 1.1 (Próxima)
- API REST con FastAPI
- Autenticación y autorización
- Dashboard web básico
- Más formatos de documentos (Excel, Word)

### Versión 2.0 (Futuro)
- Soporte multilenguaje
- Integración con sistemas CMMS
- Alertas y notificaciones
- Análisis predictivo

## 📞 Soporte

Para problemas:
1. Consulta la documentación en `docs/`
2. Revisa `CONTRIBUTING.md`
3. Crea un issue en GitHub
4. Incluye logs y pasos para reproducir

## 🎉 ¡Listo para GitHub!

El proyecto está completamente preparado para:
- ✅ Subida a GitHub
- ✅ Uso en producción
- ✅ Contribuciones de la comunidad
- ✅ Escalabilidad futura

**¡El IndustrialKnowledgeAgent está listo para revolucionar la gestión del conocimiento en mantenimiento industrial!** 🚀