#!/usr/bin/env python3
"""Script para ejecutar la aplicación Streamlit del Asistente Virtual Póliza Express.

Este script facilita el arranque de la interfaz web con configuraciones predefinidas.
"""

import sys
import os
import subprocess
from pathlib import Path

def check_streamlit_installed():
    """Verifica si Streamlit está instalado."""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def check_api_running():
    """Verifica si la API está ejecutándose."""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Función principal para ejecutar Streamlit."""
    print("🚀 Iniciando Interfaz Streamlit - Asistente Virtual Póliza Express...")
    
    # Verificar que Streamlit esté instalado
    if not check_streamlit_installed():
        print("❌ Streamlit no está instalado.")
        print("💡 Instala las dependencias con: pip install -e .")
        sys.exit(1)
    
    # Verificar que la API esté corriendo
    if not check_api_running():
        print("⚠️  La API no está ejecutándose en http://localhost:8000")
        print("💡 Asegúrate de iniciar la API primero:")
        print("   python run_api.py")
        print("\n🔄 Continuando con Streamlit (podrás ver el error en la interfaz)...")
    else:
        print("✅ API detectada y funcionando correctamente")
    
    # Configurar variables de entorno para Streamlit
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "0.0.0.0"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    # Ruta del archivo Streamlit
    streamlit_app = Path(__file__).parent / "streamlit_app.py"
    
    if not streamlit_app.exists():
        print(f"❌ No se encontró el archivo: {streamlit_app}")
        sys.exit(1)
    
    print("\n📱 Información de la aplicación:")
    print("🌐 URL: http://localhost:8501")
    print("🛡️ Título: Asistente Virtual Póliza Express")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n" + "="*60)
    print("🎯 La interfaz se abrirá automáticamente en tu navegador")
    print("⚡ Usa Ctrl+C para detener la aplicación")
    print("="*60 + "\n")
    
    try:
        # Ejecutar Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_app),
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--browser.gatherUsageStats=false",
            "--server.maxUploadSize=10"  # 10MB max upload
        ], check=True)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Aplicación detenida por el usuario")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando Streamlit: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 