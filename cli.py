#!/usr/bin/env python3
"""
IndustrialKnowledgeAgent - Interfaz de Línea de Comandos
Interfaz CLI más intuitiva para el sistema RAG
"""
import os
import sys
import argparse
import json
from pathlib import Path

# Añadir el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))


def color_print(text, color=None):
    """Imprime texto con colores (si el terminal lo soporta)"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'bold': '\033[1m',
        'end': '\033[0m'
    }
    
    if color and color in colors:
        print(f"{colors[color]}{text}{colors['end']}")
    else:
        print(text)


def print_banner():
    """Muestra el banner de bienvenida"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    IndustrialKnowledgeAgent CLI                            ║
║          Sistema RAG para Mantenimiento Industrial con Mistral AI           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    color_print(banner, 'cyan')


def print_help():
    """Muestra la ayuda detallada"""
    help_text = """
Comandos disponibles:

  setup           Inicializa el sistema con datos de ejemplo
  query <text>    Realiza una consulta al sistema
  interactive     Inicia modo interactivo (consultas en tiempo real)
  status          Muestra el estado del sistema
  
Opciones:
  --pdf-dir PATH      Directorio con PDFs para indexar
  --db NAME PATH     Base de datos SQLite (puede usarse múltiples veces)
  --no-examples      No ejecuta consultas de ejemplo al iniciar
  --api-key KEY      API Key de Mistral (alternativa a MISTRAL_API_KEY)
  
Ejemplos:
  python cli.py setup
  python cli.py query "¿Cuál es el procedimiento de mantenimiento?"
  python cli.py interactive --pdf-dir ./mis_documentos
  python cli.py --db maintenance ./data/maintenance.db --db specs ./data/specs.db
"""
    color_print(help_text, 'white')


def setup_system(pdf_dir=None, db_paths=None):
    """Inicializa el sistema con datos de ejemplo"""
    # Importar aquí para evitar cargar config al inicio
    from main import initialize_system, create_sample_databases, create_sample_pdf
    
    color_print("\n🔧 Configurando sistema...", 'yellow')
    
    # Crear datos de ejemplo si no se proporcionan
    if pdf_dir is None or db_paths is None:
        color_print("  Creando bases de datos de ejemplo...", 'blue')
        db_paths = create_sample_databases()
        color_print("  Creando PDF de ejemplo...", 'blue')
        pdf_dir = create_sample_pdf()
    
    # Inicializar sistema
    color_print("  Inicializando agentes...", 'blue')
    orchestrator = initialize_system(pdf_dir, db_paths)
    
    # Mostrar estado
    status = orchestrator.get_system_status()
    color_print("\n✅ Sistema configurado correctamente!", 'green')
    color_print(f"\nEstado:", 'bold')
    color_print(json.dumps(status, indent=2, ensure_ascii=False), 'white')
    
    return orchestrator


def run_query(orchestrator, query):
    """Ejecuta una consulta"""
    color_print(f"\n🔍 Consulta: {query}", 'yellow')
    try:
        response = orchestrator.handle_query(query)
        color_print("\n💡 Respuesta:", 'green')
        color_print("-" * 60)
        color_print(response, 'white')
        color_print("-" * 60)
    except Exception as e:
        color_print(f"\n❌ Error: {str(e)}", 'red')


def interactive_mode(orchestrator):
    """Modo interactivo"""
    color_print("\n🎯 Modo interactivo - Escribe 'exit' o 'quit' para salir", 'cyan')
    color_print("=" * 60)
    
    while True:
        try:
            query = input("\n➡️  ").strip()
            
            if query.lower() in ['exit', 'quit', 'salir']:
                color_print("\n👋 Saliendo...", 'yellow')
                break
            
            if not query:
                continue
            
            run_query(orchestrator, query)
            
        except KeyboardInterrupt:
            color_print("\n👋 Saliendo...", 'yellow')
            break
        except Exception as e:
            color_print(f"\n❌ Error: {str(e)}", 'red')


def show_status(orchestrator):
    """Muestra el estado del sistema"""
    status = orchestrator.get_system_status()
    color_print("\n📊 Estado del Sistema:", 'bold')
    color_print(json.dumps(status, indent=2, ensure_ascii=False), 'white')


def main():
    """Punto de entrada principal"""
    # Configurar parser
    parser = argparse.ArgumentParser(
        description="IndustrialKnowledgeAgent CLI - Sistema RAG para Mantenimiento Industrial",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python cli.py setup
  python cli.py query "procedimiento de mantenimiento"
  python cli.py interactive
  python cli.py --pdf-dir ./docs --db maintenance ./data/db.sqlite
"""
    )
    
    # Argumentos globales
    parser.add_argument('--pdf-dir', type=str, help='Directorio con PDFs para indexar')
    parser.add_argument('--db', action='append', nargs=2, metavar=('NAME', 'PATH'),
                        help='Base de datos SQLite: nombre y ruta')
    parser.add_argument('--no-examples', action='store_true', help='No ejecutar ejemplos')
    parser.add_argument('--api-key', type=str, help='API Key de Mistral AI')
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando setup
    setup_parser = subparsers.add_parser('setup', help='Inicializa el sistema con datos de ejemplo')
    setup_parser.add_argument('--pdf-dir', type=str, help='Directorio con PDFs para indexar')
    setup_parser.add_argument('--db', action='append', nargs=2, metavar=('NAME', 'PATH'))
    
    # Comando query
    query_parser = subparsers.add_parser('query', help='Realiza una consulta')
    query_parser.add_argument('text', type=str, help='Texto de la consulta')
    query_parser.add_argument('--pdf-dir', type=str)
    query_parser.add_argument('--db', action='append', nargs=2, metavar=('NAME', 'PATH'))
    
    # Comando interactive
    interactive_parser = subparsers.add_parser('interactive', help='Modo interactivo')
    interactive_parser.add_argument('--pdf-dir', type=str)
    interactive_parser.add_argument('--db', action='append', nargs=2, metavar=('NAME', 'PATH'))
    
    # Comando status
    status_parser = subparsers.add_parser('status', help='Muestra el estado del sistema')
    status_parser.add_argument('--pdf-dir', type=str)
    status_parser.add_argument('--db', action='append', nargs=2, metavar=('NAME', 'PATH'))
    
    args = parser.parse_args()
    
    # Si solo se pide ayuda, mostrarla sin necesidad de API key
    if args.command is None and not args.pdf_dir and not args.db and not args.api_key:
        # Verificar si se pidió ayuda explícitamente
        import sys as _sys
        if '--help' in _sys.argv or '-h' in _sys.argv:
            parser.print_help()
            sys.exit(0)
    
    # Configurar API key
    api_key = args.api_key or os.environ.get('MISTRAL_API_KEY')
    if not api_key:
        color_print("❌ Error: MISTRAL_API_KEY no configurada", 'red')
        color_print("   Configúrala con: export MISTRAL_API_KEY='tu_api_key'", 'yellow')
        color_print("   O usa: --api-key TU_API_KEY", 'yellow')
        sys.exit(1)
    
    # Configurar variable de entorno
    os.environ['MISTRAL_API_KEY'] = api_key
    
    # Procesar argumentos de bases de datos
    db_paths = {}
    if args.db:
        for name, path in args.db:
            db_paths[name] = path
    
    # Mostrar banner
    print_banner()
    
    # Inicializar sistema
    orchestrator = setup_system(args.pdf_dir, db_paths if db_paths else None)
    
    # Ejecutar comando específico
    if args.command == 'query':
        run_query(orchestrator, args.text)
    elif args.command == 'interactive':
        interactive_mode(orchestrator)
    elif args.command == 'status':
        show_status(orchestrator)
    elif args.command == 'setup' or args.command is None:
        # Si no hay comando o es setup, mostrar ayuda si no hay acción
        if args.command is None and not args.pdf_dir and not db_paths:
            print_help()
            color_print("\n💡 Usa 'python cli.py setup' para inicializar con datos de ejemplo", 'cyan')
        else:
            color_print("\n✅ Sistema inicializado. Usa 'query', 'interactive' o 'status'", 'green')
    else:
        print_help()


if __name__ == "__main__":
    main()
