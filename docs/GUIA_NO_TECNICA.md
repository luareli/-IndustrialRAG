# Guía para Usuarios No Técnicos - IndustrialRAG

> **Explicación sencilla del sistema RAG para mantenimiento industrial**

---

## 📖 ¿Qué es IndustrialRAG?

**IndustrialRAG** es un **asistente inteligente** que ayuda a encontrar información sobre mantenimiento industrial de manera rápida y fácil.

### 🎯 ¿Para qué sirve?

Imagina que tienes:
- **Manuales técnicos** en PDF (compresores, bombas, generadores)
- **Registros de mantenimiento** en bases de datos (historial, fechas, técnicos)
- **Especificaciones técnicas** (modelos, números de parte, capacidad)

En lugar de buscar manualmente en todos estos documentos, **el asistente lo hace por ti** y te da la respuesta directamente.

### 💡 Ejemplo Practico

**Pregunta:** *"¿Cuál es el procedimiento de mantenimiento para el compresor de aire?"*

**Respuesta del asistente:**
```
El procedimiento para el compresor AX-5000 es:

1. Desconectar de la red eléctrica
2. Esperar 10 minutos para enfriamiento
3. Usar guantes, gafas y calzado de seguridad
4. Verificar presión en cero
5. Cambiar filtros de aire cada 250 horas
6. Cambiar filtro de aceite cada 500 horas

Normativa: ISO 8573-1 para calidad de aire
```

---

## 🏗️ Arquitectura (Cómo Funciona Internamente)

Piensa en el sistema como un **equipo de tres expertos** que trabajan juntos:

```
┌─────────────────────────────────────────────────────────────┐
│                    TU PREGUNTA                                  │
│         "¿Qué mantenimiento tiene el equipo EQ-001?"            │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  JEFE DE EQUIPO (Orchestrator)                   │
│  Decide quién debe responder tu pregunta                       │
│                                                                │
│  "Vamos a ver... esta pregunta necesita información de         │
│   documentos Y de la base de datos"                            │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────────┴───────────────────┐
        │                                   │
        ▼                                   ▼
┌─────────────────┐             ┌─────────────────┐
│  EXPERTO EN      │             │  EXPERTO EN      │
│  DOCUMENTOS      │             │  BASE DE DATOS   │
│  (RAG Agent)     │             │  (DB Agent)      │
│                 │             │                 │
│  - Busca en     │             │  - Busca en     │
│    manuales PDF │             │    registros     │
│  - Encuentra    │             │  - Encuentra     │
│    procedimientos│             │    historiales   │
│                 │             │                 │
└─────────────────┘             └─────────────────┘
        │                                   │
        └───────────────────┬───────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  RESPUESTA FINAL                                │
│  "El equipo EQ-001 tuvo mantenimiento el 15/01/2024 y 20/03/2024.│
│   El procedimiento recomendado es..."                           │
└─────────────────────────────────────────────────────────────┘
```

### 📌 Los Tres Expertos

| Experto | Que Hace | Ejemplo de Uso |
|---------|----------|----------------|
| **RAG Agent** | Busca en documentos PDF | "¿Cuál es el procedimiento?" |
| **DB Agent** | Busca en bases de datos | "¿Cuándo fue el último mantenimiento?" |
| **Orchestrator** | Combina ambos | "Dame toda la información del equipo XYZ" |

---

## 🚀 Cómo Usarlo (Paso a Paso)

### 1️⃣ Preparación Inicial (Solo una vez)

**Alguien técnico debe:**
- Instalar el sistema en una computadora
- Cargar tus documentos PDF (manuales, guías, normativas)
- Conectar tus bases de datos (registros de mantenimiento)

**Tú solo necesitas:**
- Un navegador web o un programa para hacer preguntas

---

### 2️⃣ Hacer una Pregunta

Simplementente **escribe tu pregunta en español** como lo harías normalmente:

| Tipo de Pregunta | Ejemplo | ¿Qué Responde? |
|-----------------|---------|----------------|
| **Procedimientos** | "¿Cómo mantener un compresor?" | Te da los pasos del manual |
| **Historial** | "¿Cuándo se mantuvo EQ-001?" | Te muestra fechas y técnicos |
| **Especificaciones** | "¿Cuál es la potencia del generador?" | Te da los datos técnicos |
| **Combinada** | "Dame toda la info del compresor" | Combina manual + historial |

---

### 3️⃣ Recibir la Respuesta

El sistema te dará:
- **Respuesta directa** a tu pregunta
- **Detalles técnicos** relevantes
- **Referencias** a normativas o manuales
- **Recomendaciones** de seguridad

**Ejemplo de respuesta:**
```
RESPUESTA DIRECTA:
El compresor AX-5000 requiere mantenimiento cada 500 horas.

DETALLES TECNICOS:
- Presión máxima: 10 bar
- Flujo de aire: 5000 l/min
- Potencia: 75 kW

REFERENCIAS:
- Manual de mantenimiento: pagina 45
- Normativa: ISO 8573-1

RECOMENDACIONES:
- Usar siempre EPI (guantes, gafas, calzado de seguridad)
- Verificar presión en cero antes de empezar
```

---

## 📚 API (Interfaz para Sistemas Externos)

Si tu empresa quiere **integrar este sistema con otra aplicación** (como un sistema de tickets o ERP), esto es lo que necesitas saber:

### 🔌 Conexión Simple

Imagina que el sistema es como un **traducutor inteligente**:

```
┌─────────────────┐         ┌─────────────────┐
│   TU SISTEMA    │         │  IndustrialRAG   │
│   (ERP, Ticket)  │         │                 │
│                 │         │                 │
│  "Tengo una      │────────▶│  "Pregunta"     │
│   pregunta"      │         │                 │
│                 │         │  [Procesa...]    │
│                 │◀────────│  "Respuesta"    │
│  "Gracias!"      │         │                 │
└─────────────────┘         └─────────────────┘
```

### 📡 Métodos Disponibles (Qué puede pedir)

| Método | Que Hace | Ejemplo de Uso |
|--------|----------|----------------|
| `consultar()` | Pregunta general | "Procedimiento para bomba XYZ" |
| `consultar_documentos()` | Solo en PDFs | "Manual de seguridad" |
| `consultar_base_datos()` | Solo en registros | "Historial de EQ-001" |
| `estado()` | Ver estado del sistema | - |

### 💬 Ejemplo de Integración

Si tienes un **sistema de tickets de mantenimiento**, podrías:

1. Cuando un técnico abre un ticket sobre un equipo
2. El sistema **automáticamente pregunta** al IndustrialRAG
3. El técnico recibe **toda la información relevante** en el ticket:
   - Procedimiento del manual
   - Historial del equipo
   - Especificaciones técnicas
   - Protocolos de seguridad

---

## 📦 Librerías Usadas (Componentes del Sistema)

El sistema está construido con **herramientas de código abierto** (gratis y confiables):

### 🧠 Inteligencia Artificial

| Herramienta | Para Que | Proveedor |
|------------|----------|-----------|
| **Mistral AI** | Entiende y genera texto en español | [mistral.ai](https://mistral.ai) |
| **Sentence Transformers** | Convierte texto a números para buscar | [SBERT](https://www.sbert.net/) |

**Analogía:** Mistral AI es como un **traducutor experto**, y Sentence Transformers es como un **sistema de etiquetas inteligentes** que ayuda a encontrar información.

### 🗃️ Almacenamiento de Datos

| Herramienta | Para Que | Tipo |
|------------|----------|------|
| **Chroma** | Almacena y busca documentos PDF | Base de datos vectorial |
| **SQLite** | Almacena registros de mantenimiento | Base de datos tradicional |

**Analogía:** Chroma es como un **archivo inteligente** donde los documentos están organizados por significado, y SQLite es como un **libro de registros** tradicional.

### 📄 Procesamiento de Documentos

| Herramienta | Para Que | Formato |
|------------|----------|---------|
| **PyPDF** | Leer archivos PDF | PDF → Texto |

**Analogía:** PyPDF es como un **lector de libros digitales** que extrae el texto de los PDFs.

### 🌐 Comunicación

| Herramienta | Para Que | Uso |
|------------|----------|-----|
| **HTTP/REST** | Comunicación entre sistemas | API |

---

## 📊 ¿Qué Necesitas para Usarlo?

### Requisitos Minimos

| Requisito | Descripción | ¿Cómo Conseguirlo? |
|-----------|-------------|-------------------|
| **Computadora** | Cualquier PC moderna | Ya lo tienes |
| **Internet** | Para conectar a Mistral AI | Conexión estándar |
| **Documentos** | Tus manuales en PDF | Archivos de tu empresa |
| **Datos** | Registros de mantenimiento | Base de datos existente |

### 📋 Checklist para Empezar

- [ ] Tenemos manuales técnicos en PDF
- [ ] Tenemos registros de mantenimiento
- [ ] Alguien técnico puede instalar el sistema
- [ ] Tenemos acceso a internet
- [ ] Tenemos una API key de Mistral AI

---

## 🎯 Casos de Uso Reales

### 🏭 Fabrica de Productos

**Situación:** Un operario necesita saber cómo mantener una máquina.

**Antes:**
1. Buscar en el archivo físico (10-15 minutos)
2. Llamar al supervisor (5 minutos de espera)
3. Revisar manual PDF en la computadora (5 minutos)
4. **Total: 20+ minutos**

**Con IndustrialRAG:**
1. Preguntar: "¿Cómo mantener la máquina XYZ?"
2. **Respuesta en 10-30 segundos**

---

### 🚗 Taller Mecánico

**Situación:** Un mecánico necesita el historial de un vehículo.

**Antes:**
1. Buscar en el archivo físico (10 minutos)
2. Revisar sistema de computadora (5 minutos)
3. Llamar a recepción (5 minutos)
4. **Total: 20+ minutos**

**Con IndustrialRAG:**
1. Preguntar: "Historial del vehículo ABC-123"
2. **Respuesta inmediata con todos los datos**

---

### ⚡Beneficios Principales

| Beneficio | Impacto |
|-----------|---------|
| **Ahorro de tiempo** | 70-90% menos tiempo buscando información |
| **Reducción de errores** | Menos errores por información incorrecta |
| **Disponibilidad 24/7** | Respuestas inmediatas en cualquier momento |
| **Centralización** | Toda la información en un solo lugar |
| **Consistencia** | Todos reciben la misma información actualizada |

---

## 🔒 Seguridad

### 🛡️ Protección de Datos

El sistema es **seguro por diseño**:

✅ **Solo lectura:** No modifica tus datos, solo los lee
✅ **Validación estricta:** Bloquea consultas peligrosas
✅ **Sin acceso externo:** Todo se procesa localmente (excepto Mistral AI)
✅ **Control de acceso:** Solo quien tenga acceso a la computadora puede usarlo

### 📝 Confidencialidad

- Tus documentos **no se comparten** con nadie
- Las consultas **no se guardan** en el sistema
- Solo el **texto de tus documentos** se usa para responder

---

## 📞 Soporte y Ayuda

### 🆘 Si algo no funciona...

1. **Verifica tu pregunta:** ¿Está bien escrita?
2. **Prueba con otra pregunta:** ¿Funciona con algo más simple?
3. **Revisa los documentos:** ¿Están cargados correctamente?
4. **Pide ayuda técnica:** Si el problema persiste

### 💡 Consejos para Mejorar Resultados

✅ **Sé específico:** "Procedimiento para compresor AX-5000" > "Procedimientos"
✅ **Usa palabras clave:** "mantenimiento", "historial", "especificaciones"
✅ **Incluye números de equipo:** "EQ-001", "GEN-100KW"
❌ **Evita preguntas vagas:** "Dame información"

---

## 📝 Glosario de Términos

| Término | Significado Simple |
|---------|---------------------|
| **RAG** | Sistema que busca información y genera respuestas |
| **Chroma** | Base de datos que organiza documentos por significado |
| **API** | Forma en que los sistemas se comunican entre sí |
| **PDF** | Tipo de archivo de documento (como Word, pero universal) |
| **SQLite** | Base de datos sencilla para guardar registros |
| **Token** | Palabra o parte de una oración (usado para contar uso) |
| **Embedding** | Representación numérica de texto para búsqueda |
| **Vector Database** | Base de datos que busca por significado, no por palabras |

---

## 🎓 Analogías para Entender Mejor

| Concepto | Analogía |
|----------|----------|
| **IndustrialRAG** | Un bibliotecario experto que conoce todos tus manuales |
| **Chroma** | Un archivo con etiquetas inteligentes que ayudan a encontrar documentos |
| **Mistral AI** | Un traductor experto que entiende y genera texto en español |
| **Orchestrator** | Un jefe de equipo que decide qué experto debe responder |
| **PDF** | Un libro digital con información técnica |
| **SQLite** | Un libro de registros donde se anota todo el historial |

---

## 📌 Resumen Ejecutivo

> **IndustrialRAG** es un asistente inteligente que **encuentra información técnica de manera rápida y precisa**, combinando:
> - **Tus documentos** (manuales, guías, normativas)
> - **Tus registros** (historial, mantenimiento, especificaciones)
> - **Inteligencia artificial** para entender y generar respuestas

**Beneficios:**
- ✅ Ahorra tiempo (70-90% menos búsqueda)
- ✅ Reduce errores
- ✅ Disponible 24/7
- ✅ Centraliza toda la información
- ✅ Fácil de usar (solo haz preguntas)

**Requisitos:**
- Computadora con internet
- Documentos en PDF
- Registros en base de datos
- API key de Mistral AI

**¿Cómo empezar?**
1. Pide a tu equipo técnico que instale el sistema
2. Carga tus documentos y datos
3. Empieza a hacer preguntas

---

**¿Preguntas?** Revisa la [documentación técnica](README.md) o pide ayuda a tu equipo de TI.
