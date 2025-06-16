"""API FastAPI para el asistente virtual de análisis de Póliza Express.

Esta API proporciona endpoints para procesar consultas relacionadas con la elegibilidad
para Póliza Express utilizando el sistema de agentes de LangGraph.
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime
import uuid
import logging

# Importaciones del proyecto
from react_agent.graph import graph
from react_agent.state import InputState
from react_agent.file_manager import file_manager
from langchain_core.messages import HumanMessage

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialización de FastAPI
app = FastAPI(
    title="Asistente Virtual Póliza Express",
    description="API para consultar elegibilidad de Póliza Express usando análisis de documentos y datos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Modelos Pydantic para las requests y responses

class ConsultaRequest(BaseModel):
    """Modelo para las consultas básicas al asistente."""
    mensaje: str
    session_id: Optional[str] = None

class ConsultaResponse(BaseModel):
    """Modelo para las respuestas del asistente."""
    respuesta: str
    session_id: str
    timestamp: datetime
    estado: str
    detalles: Optional[Dict[str, Any]] = None

class StatusResponse(BaseModel):
    """Modelo para el estado de la API."""
    status: str
    version: str
    timestamp: datetime

class UploadResponse(BaseModel):
    """Modelo para respuestas de carga de archivos."""
    mensaje: str
    session_id: str
    archivos_cargados: Dict[str, str]
    timestamp: datetime

class ConsultaConArchivosRequest(BaseModel):
    """Modelo para consultas con archivos cargados."""
    session_id: str
    mensaje: Optional[str] = "Consultar elegibilidad para Póliza Express"

# Almacenamiento en memoria para sesiones (en producción usar Redis o DB)
sessions_storage = {}

@app.get("/", response_model=StatusResponse)
async def root():
    """Endpoint de estado de la API."""
    return StatusResponse(
        status="activo",
        version="1.0.0",
        timestamp=datetime.now()
    )

@app.get("/health", response_model=StatusResponse)
async def health_check():
    """Endpoint de verificación de salud de la API."""
    return StatusResponse(
        status="saludable",
        version="1.0.0", 
        timestamp=datetime.now()
    )

@app.post("/consulta", response_model=ConsultaResponse)
async def procesar_consulta(request: ConsultaRequest):
    """
    Procesa una consulta utilizando el sistema de agentes.
    
    Este endpoint ejecuta el flujo completo del asistente:
    1. Extracción de número de cédula
    2. Consulta estado en registraduría
    3. Obtención de fecha de defunción
    4. Análisis de saldo y elegibilidad para Póliza Express
    """
    try:
        # Generar session_id si no se proporciona
        session_id = request.session_id or str(uuid.uuid4())
        
        logger.info(f"Procesando consulta para sesión {session_id}: {request.mensaje}")
        
        # Crear el estado inicial (como diccionario, no como objeto InputState)
        initial_state = {
            "messages": [HumanMessage(content=request.mensaje)]
        }
        
        # Ejecutar el grafo
        logger.info("Ejecutando grafo de agentes...")
        result = await graph.ainvoke(initial_state)
        
        # Extraer la respuesta final
        if "messages" in result and result["messages"]:
            respuesta_final = result["messages"][-1].content
        else:
            respuesta_final = "No se pudo procesar la consulta"
            
        # Almacenar la sesión
        sessions_storage[session_id] = {
            "messages": result.get("messages", []),
            "timestamp": datetime.now(),
            "estado": "completado"
        }
        
        logger.info(f"Consulta procesada exitosamente para sesión {session_id}")
        
        return ConsultaResponse(
            respuesta=respuesta_final,
            session_id=session_id,
            timestamp=datetime.now(),
            estado="completado",
            detalles={
                "numero_mensajes": len(result.get("messages", [])),
                "duracion_procesamiento": "calculado_en_cliente"
            }
        )
        
    except Exception as e:
        logger.error(f"Error procesando consulta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.post("/consulta-poliza-express", response_model=ConsultaResponse)
async def consulta_poliza_express():
    """
    Endpoint específico para consultar elegibilidad de Póliza Express.
    
    Este endpoint ejecuta automáticamente todo el flujo sin requerir mensaje de entrada,
    asumiendo que los documentos ya están configurados en el sistema.
    """
    try:
        session_id = str(uuid.uuid4())
        
        logger.info(f"Iniciando consulta automática de Póliza Express para sesión {session_id}")
        
        # Mensaje estándar para activar el flujo completo
        mensaje_activacion = "Necesito consultar si una persona aplica para Póliza Express"
        
        # Crear el estado inicial (como diccionario, no como objeto InputState)
        initial_state = {
            "messages": [HumanMessage(content=mensaje_activacion)]
        }
        
        # Ejecutar el grafo
        logger.info("Ejecutando flujo completo de Póliza Express...")
        result = await graph.ainvoke(initial_state)
        
        # Extraer la respuesta final
        if "messages" in result and result["messages"]:
            respuesta_final = result["messages"][-1].content
        else:
            respuesta_final = "No se pudo completar el análisis de Póliza Express"
            
        # Almacenar la sesión
        sessions_storage[session_id] = {
            "messages": result.get("messages", []),
            "timestamp": datetime.now(),
            "estado": "completado"
        }
        
        logger.info(f"Análisis de Póliza Express completado para sesión {session_id}")
        
        return ConsultaResponse(
            respuesta=respuesta_final,
            session_id=session_id,
            timestamp=datetime.now(),
            estado="completado",
            detalles={
                "tipo_consulta": "poliza_express_automatica",
                "numero_mensajes": len(result.get("messages", []))
            }
        )
        
    except Exception as e:
        logger.error(f"Error en consulta de Póliza Express: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando Póliza Express: {str(e)}"
        )

@app.post("/upload-documentos", response_model=UploadResponse)
async def upload_documentos(
    cedula: UploadFile = File(..., description="Archivo PDF de la cédula"),
    defuncion: UploadFile = File(..., description="Archivo PDF del certificado de defunción")
):
    """
    Endpoint para cargar los documentos necesarios para el análisis.
    
    Recibe dos archivos PDF:
    - cedula: Documento de cédula de ciudadanía
    - defuncion: Certificado de defunción
    
    Retorna un session_id que se debe usar para las consultas posteriores.
    """
    try:
        session_id = str(uuid.uuid4())
        logger.info(f"Iniciando carga de documentos para sesión {session_id}")
        
        # Validar tipos de archivo
        if not cedula.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="El archivo de cédula debe ser PDF")
        
        if not defuncion.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="El archivo de certificado de defunción debe ser PDF")
        
        # Leer contenidos de archivos
        cedula_content = await cedula.read()
        defuncion_content = await defuncion.read()
        
        # Validar que los archivos no estén vacíos
        if len(cedula_content) == 0:
            raise HTTPException(status_code=400, detail="El archivo de cédula está vacío")
        
        if len(defuncion_content) == 0:
            raise HTTPException(status_code=400, detail="El archivo de certificado de defunción está vacío")
        
        # Guardar archivos usando el file manager
        cedula_path = file_manager.save_uploaded_file(
            session_id=session_id,
            file_type="cedula",
            file_content=cedula_content,
            filename=cedula.filename
        )
        
        defuncion_path = file_manager.save_uploaded_file(
            session_id=session_id,
            file_type="defuncion",
            file_content=defuncion_content,
            filename=defuncion.filename
        )
        
        # Registrar en el almacenamiento de sesiones
        sessions_storage[session_id] = {
            "archivos": {
                "cedula": cedula_path,
                "defuncion": defuncion_path
            },
            "timestamp": datetime.now(),
            "estado": "archivos_cargados"
        }
        
        logger.info(f"Documentos cargados exitosamente para sesión {session_id}")
        
        return UploadResponse(
            mensaje="Documentos cargados exitosamente",
            session_id=session_id,
            archivos_cargados={
                "cedula": cedula.filename,
                "defuncion": defuncion.filename
            },
            timestamp=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cargando documentos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al cargar documentos: {str(e)}"
        )

@app.post("/consulta-con-archivos", response_model=ConsultaResponse)
async def consulta_con_archivos(request: ConsultaConArchivosRequest):
    """
    Procesa una consulta utilizando archivos previamente cargados.
    
    Utiliza los documentos cargados en la sesión especificada para ejecutar
    el análisis completo de elegibilidad para Póliza Express.
    """
    try:
        session_id = request.session_id
        
        # Verificar que la sesión exista
        if session_id not in sessions_storage:
            raise HTTPException(
                status_code=404,
                detail="Sesión no encontrada. Primero debes cargar los documentos."
            )
        
        session_data = sessions_storage[session_id]
        
        # Verificar que los archivos estén cargados
        if "archivos" not in session_data:
            raise HTTPException(
                status_code=400,
                detail="No hay archivos cargados en esta sesión."
            )
        
        logger.info(f"Procesando consulta con archivos para sesión {session_id}")
        
        # Crear el estado inicial con información de la sesión
        initial_state = {
            "messages": [HumanMessage(content=request.mensaje)],
            "session_id": session_id  # Agregamos el session_id al estado
        }
        

        
        # Ejecutar el grafo
        logger.info("Ejecutando grafo con archivos cargados...")
        result = await graph.ainvoke(initial_state)
        
        # Extraer la respuesta final
        if "messages" in result and result["messages"]:
            respuesta_final = result["messages"][-1].content
        else:
            respuesta_final = "No se pudo procesar la consulta con los archivos cargados"
        
        # Actualizar la sesión con los resultados
        sessions_storage[session_id].update({
            "messages": result.get("messages", []),
            "timestamp": datetime.now(),
            "estado": "consulta_completada"
        })
        
        logger.info(f"Consulta con archivos completada para sesión {session_id}")
        
        return ConsultaResponse(
            respuesta=respuesta_final,
            session_id=session_id,
            timestamp=datetime.now(),
            estado="completado",
            detalles={
                "tipo_consulta": "con_archivos_cargados",
                "numero_mensajes": len(result.get("messages", [])),
                "archivos_utilizados": list(session_data["archivos"].keys())
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en consulta con archivos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando consulta con archivos: {str(e)}"
        )

@app.get("/sesion/{session_id}")
async def obtener_sesion(session_id: str):
    """
    Obtiene los detalles de una sesión específica.
    """
    if session_id not in sessions_storage:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )
    
    session_data = sessions_storage[session_id]
    
    return {
        "session_id": session_id,
        "timestamp": session_data["timestamp"],
        "estado": session_data["estado"],
        "numero_mensajes": len(session_data["messages"]),
        "mensajes": [
            {
                "tipo": type(msg).__name__,
                "contenido": msg.content if hasattr(msg, 'content') else str(msg)
            }
            for msg in session_data["messages"]
        ]
    }

@app.delete("/sesion/{session_id}")
async def eliminar_sesion(session_id: str):
    """
    Elimina una sesión específica del almacenamiento.
    """
    if session_id not in sessions_storage:
        raise HTTPException(
            status_code=404,
            detail="Sesión no encontrada"
        )
    
    del sessions_storage[session_id]
    
    return {"mensaje": f"Sesión {session_id} eliminada exitosamente"}

@app.get("/sesiones")
async def listar_sesiones():
    """
    Lista todas las sesiones activas.
    """
    return {
        "total_sesiones": len(sessions_storage),
        "sesiones": [
            {
                "session_id": session_id,
                "timestamp": data["timestamp"],
                "estado": data["estado"],
                "numero_mensajes": len(data["messages"])
            }
            for session_id, data in sessions_storage.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 