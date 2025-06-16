"""
🚀 Interfaz Streamlit para el Asistente Virtual Póliza Express

Esta aplicación permite cargar documentos (cédula y certificado de defunción)
y consultar automáticamente la elegibilidad para Póliza Express.
"""

import streamlit as st
import requests
import json
from typing import Optional
import time
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Asistente Virtual Póliza Express",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de la API
API_BASE_URL = "http://localhost:8000"

def check_api_status():
    """Verifica si la API está disponible."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_documents(cedula_file, defuncion_file):
    """Sube los documentos a la API."""
    try:
        files = {
            "cedula": ("cedula.pdf", cedula_file.getvalue(), "application/pdf"),
            "defuncion": ("defuncion.pdf", defuncion_file.getvalue(), "application/pdf")
        }
        
        response = requests.post(
            f"{API_BASE_URL}/upload-documentos",
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error subiendo documentos: {response.json().get('detail', 'Error desconocido')}")
            return None
            
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

def process_consultation(session_id: str):
    """Procesa la consulta con los documentos cargados."""
    try:
        payload = {
            "session_id": session_id,
            "mensaje": "Consultar elegibilidad para Póliza Express"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/consulta-con-archivos",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error procesando consulta: {response.json().get('detail', 'Error desconocido')}")
            return None
            
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

def get_session_details(session_id: str):
    """Obtiene los detalles de una sesión."""
    try:
        response = requests.get(f"{API_BASE_URL}/sesion/{session_id}", timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

# Interfaz principal
def main():
    # Logo y título principal
    col_logo, col_title = st.columns([1, 4])
    
    with col_logo:
        # Intentar mostrar el logo
        try:
            st.image("seguros_bolivar.png", width=120)
        except:
            # Si no existe la imagen, mostrar un placeholder
            st.markdown("🏢")
    
    with col_title:
        st.title("🛡️ Asistente Virtual Póliza Express")
        st.markdown("*Análisis automático de elegibilidad*")
    
    st.markdown("---")
    
    # Verificar estado de la API
    if not check_api_status():
        st.error("🚨 La API no está disponible. Asegúrate de que esté ejecutándose en localhost:8000")
        st.info("💡 Ejecuta: `python run_api.py` para iniciar la API")
        st.stop()
    
    st.success("✅ API conectada correctamente")
    
    # Sidebar para información
    with st.sidebar:
        st.header("📋 Información")
        st.info(
            """
            **Pasos para usar el asistente:**
            
            1. 📄 Sube la cédula de ciudadanía (PDF)
            2. 📄 Sube el certificado de defunción (PDF)
            3. 🚀 Procesa la consulta automáticamente
            4. 📊 Revisa los resultados
            
            **El sistema analizará:**
            - Número de documento
            - Estado en registraduría
            - Fecha de defunción
            - Saldo y productos financieros
            - Elegibilidad para Póliza Express
            """
        )
        
        st.markdown("---")
        st.subheader("🔗 Enlaces útiles")
        st.markdown(f"[📚 Documentación API]({API_BASE_URL}/docs)")
        st.markdown(f"[🔍 Estado de la API]({API_BASE_URL}/health)")
    
    # Columnas principales
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Carga de Documentos")
        
        # Upload de cédula
        st.subheader("1. Cédula de Ciudadanía")
        cedula_file = st.file_uploader(
            "Sube el archivo PDF de la cédula",
            type=["pdf"],
            key="cedula",
            help="Archivo PDF que contenga la cédula de ciudadanía"
        )
        
        if cedula_file:
            st.success(f"✅ Cédula cargada: {cedula_file.name}")
            st.info(f"📊 Tamaño: {len(cedula_file.getvalue())/1024:.1f} KB")
        
        # Upload de certificado de defunción
        st.subheader("2. Certificado de Defunción")
        defuncion_file = st.file_uploader(
            "Sube el archivo PDF del certificado de defunción",
            type=["pdf"],
            key="defuncion",
            help="Archivo PDF que contenga el certificado de defunción oficial"
        )
        
        if defuncion_file:
            st.success(f"✅ Certificado cargado: {defuncion_file.name}")
            st.info(f"📊 Tamaño: {len(defuncion_file.getvalue())/1024:.1f} KB")
    
    with col2:
        st.header("🚀 Procesamiento")
        
        # Mostrar estado de carga
        if cedula_file and defuncion_file:
            st.success("🎯 ¡Todos los documentos están listos!")
            
            if st.button("🚀 Procesar Análisis de Póliza Express", type="primary"):
                with st.spinner("📤 Subiendo documentos..."):
                    upload_result = upload_documents(cedula_file, defuncion_file)
                
                if upload_result:
                    session_id = upload_result["session_id"]
                    st.success(f"✅ Documentos subidos exitosamente")
                    st.info(f"🆔 ID de sesión: {session_id}")
                    
                    # Guardar session_id en el estado de la sesión
                    st.session_state["current_session_id"] = session_id
                    
                    with st.spinner("🔍 Analizando documentos y datos..."):
                        consultation_result = process_consultation(session_id)
                    
                    if consultation_result:
                        st.session_state["last_result"] = consultation_result
                        st.rerun()
        else:
            if not cedula_file:
                st.warning("⚠️ Falta cargar la cédula de ciudadanía")
            if not defuncion_file:
                st.warning("⚠️ Falta cargar el certificado de defunción")
    
    # Mostrar resultados si existen
    if "last_result" in st.session_state:
        st.markdown("---")
        st.header("📊 Resultados del Análisis")
        
        result = st.session_state["last_result"]
        
        # Información de la consulta
        col_info1, col_info2, col_info3 = st.columns(3)
        
        with col_info1:
            st.metric("🆔 ID de Sesión", result["session_id"])
        
        with col_info2:
            st.metric("📅 Fecha", result["timestamp"][:10])
        
        with col_info3:
            st.metric("⏱️ Hora", result["timestamp"][11:19])
        
        # Respuesta principal
        st.subheader("🎯 Resultado del Análisis")
        
        # Crear un contenedor expandible para la respuesta
        with st.expander("📝 Ver Respuesta Completa", expanded=True):
            st.markdown(result["respuesta"])
        
        # Detalles técnicos
        if "detalles" in result:
            st.subheader("🔧 Detalles Técnicos")
            detalles = result["detalles"]
            
            col_det1, col_det2, col_det3 = st.columns(3)
            
            with col_det1:
                st.metric("💬 Mensajes Procesados", detalles.get("numero_mensajes", "N/A"))
            
            with col_det2:
                st.metric("📁 Tipo de Consulta", detalles.get("tipo_consulta", "N/A"))
            
            with col_det3:
                archivos = detalles.get("archivos_utilizados", [])
                st.metric("📄 Archivos Utilizados", len(archivos))
        
        # Botones de acción
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🔄 Nueva Consulta"):
                # Limpiar resultados
                if "last_result" in st.session_state:
                    del st.session_state["last_result"]
                if "current_session_id" in st.session_state:
                    del st.session_state["current_session_id"]
                st.rerun()
        
        with col_btn2:
            if st.button("📋 Ver Detalles de Sesión"):
                if "current_session_id" in st.session_state:
                    session_details = get_session_details(st.session_state["current_session_id"])
                    if session_details:
                        st.json(session_details)
        
        with col_btn3:
            # Crear JSON para descarga
            result_json = json.dumps(result, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 Descargar Resultado",
                data=result_json,
                file_name=f"resultado_poliza_express_{result['session_id'][:8]}.json",
                mime="application/json"
            )

# Ejecutar la aplicación
if __name__ == "__main__":
    main() 