#!/usr/bin/env python3
"""
IndustrialKnowledgeAgent - Sistema RAG con Chroma y Mistral AI
Punto de entrada principal
"""
import os
import sys
import logging
from pathlib import Path

# Añadir el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

import chromadb

from config.settings import config, load_config
from agents.rag_agent import RAGAgent
from agents.database_agent import DatabaseQueryAgent
from agents.orchestrator import WorkflowOrchestrator


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('industrial_rag.log')
    ]
)
logger = logging.getLogger(__name__)


def initialize_system(pdf_dir: str = None, db_paths: dict = None) -> WorkflowOrchestrator:
    """
    Inicializa el sistema completo
    
    Args:
        pdf_dir: Directorio con PDFs para indexar (opcional)
        db_paths: Diccionario con rutas a bases de datos (opcional)
                  Ejemplo: {"maintenance": "data/maintenance.db"}
    
    Returns:
        Instancia de WorkflowOrchestrator inicializada
    """
    logger.info("Inicializando IndustrialKnowledgeAgent...")
    
    # Cargar configuración
    global config
    config = load_config()
    
    # Inicializar cliente Chroma
    logger.info(f"Conectando a Chroma en {config.chroma.path}")
    chroma_client = chromadb.PersistentClient(path=config.chroma.path)
    
    # Crear RAGAgent
    logger.info("Creando RAGAgent...")
    rag_agent = RAGAgent(chroma_client, config.chroma.collection_name)
    
    # Crear DatabaseQueryAgent
    logger.info("Creando DatabaseQueryAgent...")
    db_agent = DatabaseQueryAgent()
    
    # Cargar PDFs si se especifica directorio
    if pdf_dir:
        logger.info(f"Cargando PDFs desde {pdf_dir}...")
        chunks_processed = rag_agent.load_pdfs(pdf_dir)
        logger.info(f"Procesados {chunks_processed} chunks de documentación")
    
    # Cargar bases de datos si se especifican
    if db_paths:
        logger.info("Cargando bases de datos...")
        for db_name, db_path in db_paths.items():
            db_agent.add_connection(db_name, db_path)
            logger.info(f"Base de datos {db_name} cargada desde {db_path}")
    
    # Crear orchestrator
    orchestrator = WorkflowOrchestrator(rag_agent, db_agent)
    
    logger.info("Sistema inicializado correctamente")
    return orchestrator


def create_sample_databases():
    """Crea bases de datos de ejemplo para pruebas"""
    from utils.database_utils import initialize_database
    
    # Base de datos de mantenimiento
    maintenance_schema = """
    CREATE TABLE IF NOT EXISTS maintenance_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id TEXT NOT NULL,
        equipment_name TEXT NOT NULL,
        maintenance_date TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'COMPLETED',
        technician TEXT,
        cost REAL DEFAULT 0.0
    );
    
    CREATE TABLE IF NOT EXISTS equipment (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        model TEXT,
        manufacturer TEXT,
        installation_date TEXT,
        last_maintenance TEXT,
        status TEXT DEFAULT 'ACTIVE'
    );
    
    INSERT OR IGNORE INTO equipment (id, name, model, manufacturer, installation_date, status)
    VALUES
        ('EQ-001', 'Compresor de Aire', 'AX-5000', 'Atlas Copco', '2022-01-15', 'ACTIVE'),
        ('EQ-002', 'Bombas de Agua', 'BP-200', 'Grundfos', '2021-11-03', 'ACTIVE'),
        ('EQ-003', 'Generador Eléctrico', 'GEN-100KW', 'Caterpillar', '2023-02-20', 'MAINTENANCE'),
        ('EQ-004', 'Sistema de Refrigeración', 'CR-45', 'Carrier', '2022-05-10', 'ACTIVE');
    
    INSERT OR IGNORE INTO maintenance_logs (equipment_id, equipment_name, maintenance_date, description, status, technician, cost)
    VALUES
        ('EQ-001', 'Compresor de Aire', '2024-01-15', 'Cambio de filtros de aire y aceite', 'COMPLETED', 'Juan Pérez', 250.0),
        ('EQ-001', 'Compresor de Aire', '2024-03-20', 'Inspección general y lubricación', 'COMPLETED', 'Carlos López', 180.0),
        ('EQ-002', 'Bombas de Agua', '2024-02-10', 'Cambio de sellos mecánicos', 'COMPLETED', 'Ana García', 450.0),
        ('EQ-003', 'Generador Eléctrico', '2024-04-01', 'Cambio de aceite y filtros', 'PENDING', 'Luis Martínez', 320.0);
    """
    
    # Base de datos de especificaciones técnicas
    specs_schema = """
    CREATE TABLE IF NOT EXISTS technical_specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id TEXT NOT NULL,
        spec_name TEXT NOT NULL,
        value TEXT,
        unit TEXT,
        description TEXT,
        UNIQUE(equipment_id, spec_name)
    );
    
    CREATE TABLE IF NOT EXISTS safety_protocols (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        protocol_name TEXT NOT NULL,
        description TEXT,
        applicable_equipment TEXT,
        steps TEXT
    );
    
    INSERT OR IGNORE INTO technical_specs (equipment_id, spec_name, value, unit, description)
    VALUES
        ('EQ-001', 'Presión Máxima', '10', 'bar', 'Presión máxima de operación'),
        ('EQ-001', 'Flujo de Aire', '5000', 'l/min', 'Capacidad de flujo de aire'),
        ('EQ-001', 'Potencia', '75', 'kW', 'Potencia del motor'),
        ('EQ-002', 'Flujo de Agua', '200', 'm3/h', 'Capacidad de bombeo'),
        ('EQ-002', 'Altura Máxima', '50', 'm', 'Altura máxima de bombeo'),
        ('EQ-003', 'Potencia', '100', 'kW', 'Potencia del generador'),
        ('EQ-003', 'Voltaje', '400', 'V', 'Voltaje de salida'),
        ('EQ-004', 'Temperatura', '-20 a 10', '°C', 'Rango de temperatura');
    
    INSERT OR IGNORE INTO safety_protocols (protocol_name, description, applicable_equipment, steps)
    VALUES
        ('Mantenimiento Compresor', 'Protocolo para mantenimiento seguro de compresores', 'EQ-001', '1. Desconectar de la red eléctrica. 2. Esperar 10 minutos para enfriamiento. 3. Usar EPI adecuado. 4. Verificar presión en cero.'),
        ('Mantenimiento Bomba', 'Protocolo para mantenimiento de bombas de agua', 'EQ-002', '1. Cerrar válvulas de entrada/salida. 2. Drenar el sistema. 3. Usar guantes de protección. 4. Verificar que no haya presión residual.');
    """
    
    db_paths = {
        "maintenance": "data/maintenance_db.sqlite",
        "specs": "data/technical_specifications_db.sqlite"
    }
    
    for db_name, db_path in db_paths.items():
        schema = maintenance_schema if db_name == "maintenance" else specs_schema
        initialize_database(db_path, schema)
        logger.info(f"Base de datos de ejemplo creada: {db_path}")
    
    return db_paths


def create_sample_pdf():
    """Crea un PDF de ejemplo para pruebas"""
    from fpdf import FPDF
    
    # Crear directorio de datos si no existe
    Path("data/pdfs").mkdir(parents=True, exist_ok=True)
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Contenido de ejemplo
    content = """
    MANUAL DE MANTENIMIENTO INDUSTRIAL
    
    1. INTRODUCCION
    
    Este manual describe los procedimientos de mantenimiento para equipos industriales.
    
    2. MANTENIMIENTO DE COMPRESORES DE AIRE
    
    Los compresores de aire requieren mantenimiento regular cada 500 horas de operación
    o cada 6 meses, lo que ocurra primero.
    
    Procedimiento de mantenimiento preventivo:
    - Verificar niveles de aceite
    - Cambiar filtros de aire cada 250 horas
    - Cambiar filtro de aceite cada 500 horas
    - Inspeccionar correas y tensiones
    - Limpiar radiador
    
   Normativa aplicable: ISO 8573-1 para calidad de aire comprimido.
    
    3. MANTENIMIENTO DE BOMBAS DE AGUA
    
    Las bombas de agua requieren:
    - Lubricación mensual de rodamientos
    - Cambio de sellos mecánicos cada 2000 horas
    - Verificación de alineación cada 3 meses
    
    4. PROTOCOLOS DE SEGURIDAD
    
    Antes de cualquier intervención:
    - Bloqueo/etiquetado (LOTO) obligatorio
    - Uso de EPI: guantes, gafas, calzado de seguridad
    - Verificar que el equipo esté frío y sin presión
    
    5. REGISTROS
    
    Todos los mantenimientos deben ser registrados en el sistema de gestión
    con fecha, hora, técnico responsable y observaciones.
    """
    
    pdf.multi_cell(0, 10, txt=content)
    pdf_path = "data/pdfs/manual_mantenimiento.pdf"
    pdf.output(pdf_path)
    
    logger.info(f"PDF de ejemplo creado: {pdf_path}")
    return "data/pdfs"


def main(pdf_dir: str = None, db_paths: dict = None, run_examples: bool = True):
    """Función principal de ejecución
    
    Args:
        pdf_dir: Directorio con PDFs para indexar (si None, usa ejemplos)
        db_paths: Diccionario de rutas a bases de datos (si None, usa ejemplos)
        run_examples: Si True, ejecuta consultas de ejemplo
    """
    logger.info("IndustrialKnowledgeAgent - Inicio")
    
    # Verificar API key
    if not os.environ.get("MISTRAL_API_KEY"):
        logger.error("MISTRAL_API_KEY no configurada. Por favor configura la variable de entorno.")
        logger.error("Puedes obtener una API key en: https://console.mistral.ai/api-keys/")
        sys.exit(1)
    
    # Usar datos proporcionados o crear ejemplos
    if pdf_dir is None or db_paths is None:
        logger.info("No se proporcionaron rutas, usando datos de ejemplo...")
        create_sample_databases()
        pdf_dir = create_sample_pdf()
        db_paths = {
            "maintenance": "data/maintenance_db.sqlite",
            "specs": "data/technical_specifications_db.sqlite"
        }
    
    # Inicializar sistema
    orchestrator = initialize_system(pdf_dir, db_paths)
    
    # Mostrar estado del sistema
    status = orchestrator.get_system_status()
    logger.info(f"Estado del sistema: {json.dumps(status, indent=2)}")
    
    # Ejecutar ejemplos solo si se solicita
    if run_examples:
        logger.info("\n" + "="*50)
        logger.info("EJEMPLOS DE CONSULTAS")
        logger.info("="*50)
        
        examples = [
            "¿Cuál es el procedimiento de mantenimiento para el compresor de aire?",
            "Muestra el historial de mantenimiento del equipo EQ-001",
            "¿Cuáles son las especificaciones técnicas del generador GEN-100KW?",
            "¿Qué protocolos de seguridad debo seguir para mantener una bomba de agua?"
        ]
        
        for i, query in enumerate(examples, 1):
            logger.info(f"\n[{i}] Consulta: {query}")
            try:
                response = orchestrator.handle_query(query)
                logger.info(f"Respuesta:\n{response}\n")
            except Exception as e:
                logger.error(f"Error en consulta {i}: {str(e)}")
        
        logger.info("\n" + "="*50)
        logger.info("Ejecución completada. El sistema está listo para usar.")
        logger.info("="*50)
    else:
        logger.info("Sistema inicializado en modo producción. Listo para consultas.")
    
    return orchestrator


if __name__ == "__main__":
    import argparse
    
    # Configurar argument parser
    parser = argparse.ArgumentParser(description="IndustrialKnowledgeAgent - Sistema RAG para Mantenimiento Industrial")
    parser.add_argument("--pdf-dir", type=str, help="Directorio con PDFs para indexar")
    parser.add_argument("--db-path", action="append", nargs=2, metavar=("NAME", "PATH"), 
                        help="Base de datos SQLite: nombre y ruta (ej: maintenance data/maintenance.db)")
    parser.add_argument("--no-examples", action="store_true", help="No ejecutar consultas de ejemplo")
    parser.add_argument("--interactive", action="store_true", help="Modo interactivo para producción")
    
    args = parser.parse_args()
    
    # Procesar argumentos de bases de datos
    db_paths = {}
    if args.db_path:
        for name, path in args.db_path:
            db_paths[name] = path
    
    # Inicializar sistema
    orchestrator = main(
        pdf_dir=args.pdf_dir,
        db_paths=db_paths if db_paths else None,
        run_examples=not args.no_examples
    )
    
    # Modo interactivo para producción
    if args.interactive:
        logger.info("\n" + "="*50)
        logger.info("MODO INTERACTIVO (Ctrl+C para salir)")
        logger.info("="*50)
        while True:
            try:
                query = input("\nConsulta: ")
                if not query.strip():
                    continue
                response = orchestrator.handle_query(query)
                print("\n" + "-"*50)
                print(response)
                print("-"*50)
            except KeyboardInterrupt:
                logger.info("\nSaliendo...")
                break
            except Exception as e:
                logger.error(f"Error: {str(e)}")
