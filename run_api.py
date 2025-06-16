#!/usr/bin/env python3
"""Script para ejecutar la API del Asistente Virtual Póliza Express.

Este script facilita el arranque del servidor API con diferentes configuraciones.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio src al Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Función principal para ejecutar el servidor."""
    try:
        from react_agent.server import run_server
        print("🚀 Iniciando API del Asistente Virtual Póliza Express...")
        print("📚 Documentación disponible en: http://localhost:8000/docs")
        print("🔧 Panel de administración: http://localhost:8000/redoc")
        print("⚡ Estado de la API: http://localhost:8000/health")
        print("\n" + "="*60)
        
        run_server()
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("\n💡 Asegúrate de que todas las dependencias estén instaladas:")
        print("   pip install -e .")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 