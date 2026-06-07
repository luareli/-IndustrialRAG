# Guía de Instalación - IndustrialRAG

> Instrucciones detalladas para instalar y configurar el sistema

---

## 📋 Requisitos del Sistema

### Sistema Operativo

| SO | Versión Mínima | Notas |
|-----|----------------|-------|
| Linux | Ubuntu 20.04+ / CentOS 8+ | Recomendado para producción |
| macOS | 11.0+ (Big Sur) | Funciona con Python nativo |
| Windows | 10 / 11 | Usar WSL2 para mejor rendimiento |

### Hardware

| Componente | Requisito Mínimo | Recomendado |
|------------|-------------------|-------------|
| CPU | 2 núcleos | 4+ núcleos |
| RAM | 4 GB | 8+ GB (para embeddings grandes) |
| Almacenamiento | 10 GB libres | 20+ GB (para datasets grandes) |
| GPU | No requerida | Opcional (acelera embeddings) |

### Python

- **Versión:** Python 3.9, 3.10, 3.11, o 3.12
- **Recomendación:** Python 3.10 o 3.11 para mejor compatibilidad

**Verificar versión:**
```bash
python3 --version
# Debe mostrar: Python 3.9.x o superior
```

---

## 🛠️ Instalación Paso a Paso

### Opción 1: Instalación Estándar (Recomendada)

#### 1. Clonar el repositorio

```bash
# Navegar al directorio de trabajo
cd /ruta/a/tu/proyecto

# Clonar el repositorio
git clone https://github.com/tu-usuario/IndustrialRAG.git
cd IndustrialRAG
cd IndustrialRAG

# Si estás trabajando con archivos locales, simplemente copialos
tar -xzvf IndustrialRAG.tar.gz
cd IndustrialRAG
```

#### 2. Crear entorno virtual

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar el entorno
# Linux/macOS:
source venv/bin/activate

# Windows (PowerShell):
.\venv\Scripts\Activate

# Windows (CMD):
venv\Scripts\activate
```

**Verificar que el entorno está activo:**
```bash
# El prompt debe mostrar (venv) al inicio
which python3  # Linux/macOS
where python  # Windows
# Debe mostrar la ruta dentro del directorio venv
```

#### 3. Instalar dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Instalación con logging detallado (opcional):**
```bash
pip install --upgrade pip --verbose
pip install -r requirements.txt --verbose
```

#### 4. Instalar dependencias de embeddings

El modelo `all-MiniLM-L6-v2` se instalará automáticamente con las dependencias.

**Nota:** La primera vez que se usa, se descargará automáticamente el modelo (aproximadamente 90MB).

#### 5. Configurar API Key de Mistral

Crear un archivo `.env` en el directorio raíz:

```bash
# Crear archivo .env
echo "MISTRAL_API_KEY=tu_api_key_de_mistral" > .env

# Cargar variables de entorno (Linux/macOS)
source .env

# Para Windows, editar el archivo y luego:
# PowerShell: Get-Content .env | ForEach-Object { $_.Split('=') | Set-Variable -Name $_[0] -Value $_[1] }
```

**Alternativa: Variables de entorno directas**

```bash
# Linux/macOS
export MISTRAL_API_KEY="tu_api_key_de_mistral"

# Windows (PowerShell)
$env:MISTRAL_API_KEY = "tu_api_key_de_mistral"

# Windows (CMD)
set MISTRAL_API_KEY=tu_api_key_de_mistral
```

**Para hacer permanente la variable:**

```bash
# Linux/macOS - añadir a ~/.bashrc o ~/.zshrc
echo 'export MISTRAL_API_KEY="tu_api_key_de_mistral"' >> ~/.bashrc
source ~/.bashrc

# Windows - Variables de entorno del sistema
# Panel de Control > Sistema > Configuración avanzada > Variables de entorno
```

#### 6. Verificar instalación

```bash
# Verificar que todos los paquetes están instalados
pip list | grep -E "(mistralai|chromadb|sentence|pypdf)"

# Probar importación de módulos
python3 -c "import mistralai; import chromadb; import sentence_transformers; print('Todos los módulos se importan correctamente')"
```

---

### Opción 2: Instalación con Docker (Para Producción)

#### 1. Crear Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar archivos
COPY IndustrialRAG/ /app/IndustrialRAG/
COPY requirements.txt /app/

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Configurar entrada
ENTRYPOINT ["python3", "IndustrialRAG/main.py"]

# Variable de entorno (se pasa en tiempo de ejecución)
ENV MISTRAL_API_KEY=""
```

#### 2. Construir imagen

```bash
docker build -t industrial-rag .
```

#### 3. Ejecutar contenedor

```bash
docker run -it --rm \
  -e MISTRAL_API_KEY="tu_api_key_de_mistral" \
  -v $(pwd)/IndustrialRAG/data:/app/IndustrialRAG/data \
  industrial-rag
```

**Explicación de opciones:**
- `-it`: Modo interactivo
- `--rm`: Eliminar contenedor después de salir
- `-e`: Pasar variable de entorno
- `-v`: Montar volumen para persistencia de datos

---

## 📦 Dependencias Opcionales

### Para desarrollo

```bash
# Herramientas de desarrollo
pip install pytest pytest-cov flake8 black isort

# Para generación de PDFs de ejemplo
pip install fpdf2

# Para logging avanzado
pip install python-json-logger
```

### Modelos de embeddings alternativos

El sistema usa `all-MiniLM-L6-v2` por defecto (90MB, buen balance velocidad/calidad).

**Alternativas:**

```bash
# BAAI/bge-small-en-v1.5 (mejor calidad, 128MB)
pip install sentence-transformers

# Para usar un modelo diferente, edita config/settings.py:
# embedding_model = "BAAI/bge-small-en-v1.5"
```

| Modelo | Tamaño | Calidad | Velocidad |
|--------|--------|---------|-----------|
| all-MiniLM-L6-v2 | 90MB | Media | Rápida |
| BAAI/bge-small-en-v1.5 | 128MB | Alta | Media |
| all-mpnet-base-v2 | 420MB | Muy Alta | Lenta |

---

## 🔧 Configuración de Chroma

Chroma almacena los índices vectoriales en disco de forma persistente.

### Ubicación por defecto
- Directorio: `./chroma_db/` (relativo al directorio de ejecución)

### Personalizar ubicación

```python
# En config/settings.py
ChromaConfig(path="/ruta/personalizada/chroma_db")
```

**Recomendaciones:**
- Usar disco SSD para mejor rendimiento
- Asegurar que el directorio tenga al menos 10GB libres
- Para producción: montar en volumen Docker o almacenamiento cloud

### Limpiar caché de Chroma

```bash
# Eliminar base de datos Chroma existente
rm -rf chroma_db/

# O para ubicación personalizada
rm -rf /ruta/personalizada/chroma_db/
```

---

## ⚡ Optimización de Rendimiento

### Para datasets grandes

1. **Aumentar tamaño de chunks:**
```python
# En config/settings.py
ChromaConfig(chunk_size=2000, chunk_overlap=400)
```

2. **Usar modelo de embeddings más eficiente:**
```python
# Modelos más rápidos (menor precisión)
# embedding_model = "all-MiniLM-L6-v2"  # 90MB, rápido
# embedding_model = "paraphrase-MiniLM-L6-v2"  # 80MB, muy rápido
```

3. **Limitar número de resultados:**
```python
# En las consultas
rag_agent.search(query, top_k=5)  # En lugar de top_k=3
```

### Para producción

1. **Usar Chroma Server (recomendado para múltiples usuarios):**
```bash
# Instalar Chroma Server
docker pull chromadb/chroma

# Ejecutar
docker run -p 8000:8000 chromadb/chroma

# Conectar desde el cliente
chroma_client = chromadb.HttpClient(host="localhost", port=8000)
```

2. **Configurar índice en memoria para pruebas rápidas:**
```python
# En lugar de PersistentClient
chroma_client = chromadb.Client()  # In-memory
```

---

## 🧪 Verificación de la Instalación

### Test rápido

```bash
python3 -c "
from main import initialize_system
import os

# Configurar API key
os.environ['MISTRAL_API_KEY'] = 'test_key'

try:
    orchestrator = initialize_system()
    print('✓ Sistema inicializado correctamente')
except Exception as e:
    print(f'✗ Error: {str(e)}')
"
```

**Salida esperada:**
```
✓ Sistema inicializado correctamente
```

### Test de conectividad con Mistral

```bash
python3 -c "
import os
from mistralai import Mistral

os.environ['MISTRAL_API_KEY'] = 'tu_api_key_de_mistral'
client = Mistral()

try:
    response = client.chat(model='mistral-small-latest', messages=[{'role': 'user', 'content': 'Hola'}])
    print('✓ Conexión con Mistral AI funcionando')
except Exception as e:
    print(f'✗ Error de conexión: {str(e)}')
"
```

### Test de Chroma

```bash
python3 -c "
import chromadb

try:
    client = chromadb.PersistentClient(path='./test_chroma')
    collection = client.create_collection(name='test')
    collection.add(documents=['test doc'], ids=['id1'])
    results = collection.query(query_texts=['test'], n_results=1)
    print('✓ Chroma funcionando correctamente')
    import shutil
    shutil.rmtree('./test_chroma')
except Exception as e:
    print(f'✗ Error con Chroma: {str(e)}')
"
```

---

## 📝 Configuración de Bases de Datos

### Crear bases de datos desde cero

El sistema puede inicializar bases de datos SQLite automáticamente:

```python
from utils.database_utils import initialize_database

# Esquema de ejemplo
schema = '''
CREATE TABLE equipment (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
'''

# Crear base de datos
conn = initialize_database('mi_database.db', schema)
```

### Importar datos existentes

```python
import sqlite3
from agents.database_agent import DatabaseQueryAgent

# Conectar a base de datos existente
conn = sqlite3.connect('tu_base_de_datos.db')

# Crear agente
db_agent = DatabaseQueryAgent(db_connections={'mi_db': conn})
```

---

## 🎯 Solución de Problemas Comunes

| Problema | Causa | Solución |
|----------|-------|----------|
| `ModuleNotFoundError: mistralai` | Paquete no instalado | `pip install mistralai` |
| `No module named 'sentence_transformers'` | Dependencia faltante | `pip install sentence-transformers` |
| `MISTRAL_API_KEY not configured` | Variable de entorno no configurada | Configurar API key |
| `Chroma error: path not writable` | Permisos insuficientes | `chmod 755 chroma_db/` |
| `Out of memory` | Dataset demasiado grande | Reducir chunk_size o usar modelo más pequeño |
| `Rate limit exceeded` | Demasiadas peticiones a Mistral | Implementar retry con backoff |

### Errores específicos

#### Error: `import chromadb` falla
```bash
# Reinstalar con dependencias
pip uninstall chromadb -y
pip install chromadb==0.5.0
```

#### Error: Modelos de embeddings no se descargan
```bash
# Forzar descarga
python3 -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2')"
```

#### Error: Problemas con PyPDF
```bash
# Instalar versiones específicas
pip uninstall pypdf -y
pip install pypdf==4.0.0
```

---

## 📊 Métricas de Instalación

Para monitorear el uso de recursos:

```bash
# Tamaño de Chroma DB
du -sh chroma_db/

# Uso de memoria
free -h  # Linux
vm_stat  # macOS

# Uso de CPU
htop  # Linux
Activity Monitor  # macOS
```

---

## 🔄 Actualización

Para actualizar a una nueva versión:

```bash
# Si usas git
git pull origin main
pip install -r requirements.txt --upgrade

# Si no usas git
# Descargar nueva versión y reemplazar archivos
pip install -r requirements.txt --upgrade
```

---

## 📞 Soporte Adicional

Si encuentras problemas no cubiertos en esta guía:

1. **Verifica los logs:** `cat industrial_rag.log`
2. **Revisa la documentación:** [README.md](../README.md)
3. **Prueba con datos mínimos:** Usa solo 1-2 PDFs pequeños
4. **Contacta al equipo de desarrollo:** (si aplica)

---

## ✅ Checklist de Instalación

- [ ] Python 3.9+ instalado
- [ ] Entorno virtual creado y activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] API Key de Mistral configurada
- [ ] Chroma funcionando (`chroma_db/` creado)
- [ ] Test de conexión con Mistral exitoso
- [ ] Test de Chroma exitoso
- [ ] Base de datos de ejemplo creada
- [ ] PDF de ejemplo generado

---

**¡Listo!** Ahora puedes usar el IndustrialRAG.

Siguiente paso: [Guía de Uso](USO.md)
