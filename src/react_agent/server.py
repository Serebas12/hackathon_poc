"""Servidor principal para la API del asistente virtual Póliza Express.

Este módulo configura y ejecuta el servidor FastAPI con todas las configuraciones necesarias.
"""

import uvicorn
import os
from pathlib import Path
import logging
from react_agent.api import app

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_server_config():
    """Obtiene la configuración del servidor desde variables de entorno."""
    return {
        "host": os.getenv("HOST", "0.0.0.0"),
        "port": int(os.getenv("PORT", 8000)),
        "reload": os.getenv("RELOAD", "false").lower() == "true",
        "workers": int(os.getenv("WORKERS", 1)),
        "log_level": os.getenv("LOG_LEVEL", "info"),
    }

def run_server():
    """Ejecuta el servidor con la configuración especificada."""
    config = get_server_config()
    
    logger.info("Iniciando servidor del Asistente Virtual Póliza Express")
    logger.info(f"Configuración: {config}")
    
    # Verificar que los archivos de credenciales existan
    creds_path = "/home/jssaa/proyectos/react-agent/src/creds/credentials.json"
    if not os.path.exists(creds_path):
        logger.warning(f"Archivo de credenciales no encontrado en: {creds_path}")
    
    # Verificar que los documentos de prueba existan
    doc_path = "/home/jssaa/proyectos/react-agent/src/doc_pruebas"
    if not os.path.exists(doc_path):
        logger.warning(f"Directorio de documentos de prueba no encontrado: {doc_path}")
    
    try:
        uvicorn.run(
            "react_agent.api:app",
            host=config["host"],
            port=config["port"],
            reload=config["reload"],
            workers=config["workers"] if not config["reload"] else 1,
            log_level=config["log_level"],
            access_log=True
        )
    except Exception as e:
        logger.error(f"Error al iniciar el servidor: {e}")
        raise

if __name__ == "__main__":
    run_server() 