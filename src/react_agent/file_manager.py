"""Gestor de archivos temporales para el manejo de documentos cargados.

Este módulo proporciona funcionalidades para gestionar archivos temporales
de cédulas y certificados de defunción cargados por los usuarios.
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional
import logging
from datetime import datetime, timedelta
import threading
import time

logger = logging.getLogger(__name__)

class FileManager:
    """Gestor de archivos temporales con limpieza automática."""
    
    def __init__(self, temp_dir: str = None, cleanup_interval: int = 3600):
        """
        Inicializa el gestor de archivos.
        
        Args:
            temp_dir: Directorio temporal base (None para usar el del sistema)
            cleanup_interval: Intervalo en segundos para limpieza automática
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self.base_path = Path(self.temp_dir) / "react_agent_uploads"
        self.base_path.mkdir(exist_ok=True)
        self.cleanup_interval = cleanup_interval
        
        # Almacenamiento de archivos por sesión
        self.session_files: Dict[str, Dict[str, str]] = {}
        
        # Iniciar limpieza automática
        self._start_cleanup_thread()
        
        logger.info(f"FileManager inicializado en: {self.base_path}")
    
    def save_uploaded_file(self, session_id: str, file_type: str, file_content: bytes, filename: str) -> str:
        """
        Guarda un archivo cargado y retorna la ruta.
        
        Args:
            session_id: ID de la sesión
            file_type: Tipo de archivo ('cedula' o 'defuncion')
            file_content: Contenido del archivo en bytes
            filename: Nombre original del archivo
            
        Returns:
            str: Ruta del archivo guardado
        """
        # Crear directorio de sesión
        session_dir = self.base_path / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Generar nombre de archivo único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(filename).suffix
        safe_filename = f"{file_type}_{timestamp}{file_extension}"
        
        file_path = session_dir / safe_filename
        
        # Guardar archivo
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Registrar en el almacenamiento de sesión
        if session_id not in self.session_files:
            self.session_files[session_id] = {}
        
        self.session_files[session_id][file_type] = str(file_path)
        
        logger.info(f"Archivo guardado: {file_path}")
        return str(file_path)
    
    def get_file_path(self, session_id: str, file_type: str) -> Optional[str]:
        """
        Obtiene la ruta de un archivo de sesión.
        
        Args:
            session_id: ID de la sesión
            file_type: Tipo de archivo ('cedula' o 'defuncion')
            
        Returns:
            Optional[str]: Ruta del archivo o None si no existe
        """
        return self.session_files.get(session_id, {}).get(file_type)
    
    def cleanup_session(self, session_id: str):
        """
        Limpia los archivos de una sesión específica.
        
        Args:
            session_id: ID de la sesión a limpiar
        """
        if session_id in self.session_files:
            session_dir = self.base_path / session_id
            if session_dir.exists():
                shutil.rmtree(session_dir)
            del self.session_files[session_id]
            logger.info(f"Sesión limpiada: {session_id}")
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Limpia archivos antiguos.
        
        Args:
            max_age_hours: Edad máxima de archivos en horas
        """
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for session_dir in self.base_path.iterdir():
            if session_dir.is_dir():
                # Verificar si el directorio es muy antiguo
                dir_mtime = datetime.fromtimestamp(session_dir.stat().st_mtime)
                if dir_mtime < cutoff_time:
                    session_id = session_dir.name
                    self.cleanup_session(session_id)
                    logger.info(f"Directorio antiguo limpiado: {session_dir}")
    
    def _start_cleanup_thread(self):
        """Inicia el hilo de limpieza automática."""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(self.cleanup_interval)
                    self.cleanup_old_files()
                except Exception as e:
                    logger.error(f"Error en limpieza automática: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("Hilo de limpieza automática iniciado")
    
    def get_session_info(self, session_id: str) -> Dict[str, str]:
        """
        Obtiene información de archivos de una sesión.
        
        Args:
            session_id: ID de la sesión
            
        Returns:
            Dict[str, str]: Información de archivos de la sesión
        """
        return self.session_files.get(session_id, {}).copy()

# Instancia global del gestor de archivos
file_manager = FileManager() 