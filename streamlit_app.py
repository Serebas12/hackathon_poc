
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

# CSS Personalizado - Colores Corporativos Seguros Bolívar
st.markdown("""
<style>
    /* Importar fuentes de Google */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS para colores corporativos */
    :root {
        --verde-bolivar: #018548;
        --amarillo-dorado: #F4B51A;
        --verde-claro: #02a055;
        --amarillo-claro: #f5c332;
        --verde-oscuro: #016639;
        --amarillo-oscuro: #d99c15;
        --blanco: #ffffff;
        --gris-claro: #f8f9fa;
        --gris-medio: #6c757d;
        --gris-oscuro: #343a40;
    }
    
    /* Animaciones personalizadas */
    @keyframes slideInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }
    
    /* Fondo principal - Verde Bolívar sólido */
    .stApp {
        background: var(--verde-bolivar);
        background-attachment: fixed;
        min-height: 100vh;
        animation: fadeIn 1s ease-in;
    }
    
    .main > div {
        background: var(--verde-bolivar);
        background-attachment: fixed;
        min-height: 100vh;
    }
    
    /* Fondo de toda la aplicación */
    .css-18e3th9, .css-k1vhr4 {
        background: var(--verde-bolivar) !important;
    }
    
    /* Fondo del contenedor principal de Streamlit */
    .css-fg4pbf, .css-1lcbmhc, .css-1y4p8pa {
        background: var(--verde-bolivar) !important;
    }
    
    /* Contenedor principal con efectos modernos */
    .block-container {
        background: rgba(255, 255, 255, 0.97);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 
            0 20px 40px rgba(1, 133, 72, 0.15),
            0 10px 20px rgba(244, 181, 26, 0.1);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin: 1rem auto;
        max-width: 1200px;
        animation: slideInUp 0.8s ease-out;
        transition: all 0.3s ease;
    }
    
    .block-container:hover {
        box-shadow: 
            0 25px 50px rgba(1, 133, 72, 0.2),
            0 15px 30px rgba(244, 181, 26, 0.15);
        transform: translateY(-2px);
    }
    
    /* Fondo completo - selectores adicionales */
    html, body, [data-testid="stAppViewContainer"] {
        background: var(--verde-bolivar) !important;
    }
    
    /* Fondo del área principal */
    [data-testid="stAppViewContainer"] > .main {
        background: var(--verde-bolivar) !important;
    }
    
    /* Sidebar con colores corporativos */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--verde-bolivar) 0%, var(--verde-claro) 100%) !important;
        border-right: 3px solid var(--amarillo-dorado);
    }
    
    /* Contenedor de la sidebar */
    [data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, var(--verde-bolivar) 0%, var(--verde-claro) 100%) !important;
    }
    
    /* Títulos con animación y colores corporativos */
    h1 {
        color: var(--verde-bolivar);
        text-shadow: 2px 2px 4px rgba(1, 133, 72, 0.2);
        border-bottom: 4px solid var(--amarillo-dorado);
        padding-bottom: 15px;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        position: relative;
        animation: slideInUp 1s ease-out 0.2s both;
    }
    
    h1::after {
        content: '';
        position: absolute;
        bottom: -4px;
        left: 0;
        width: 0;
        height: 4px;
        background: var(--verde-bolivar);
        animation: shimmer 2s infinite;
        background: linear-gradient(90deg, transparent, var(--verde-bolivar), transparent);
        background-size: 200px 100%;
    }
    
    /* Subtítulos */
    h2, h3 {
        color: var(--verde-oscuro);
        margin-top: 2rem;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        position: relative;
        animation: slideInUp 0.8s ease-out;
    }
    
    h2::before {
        content: '';
        position: absolute;
        left: -10px;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 20px;
        background: var(--amarillo-dorado);
        border-radius: 2px;
    }
    
    /* Botones con diseño corporativo y microinteracciones */
    .stButton > button {
        background: linear-gradient(45deg, var(--verde-bolivar), var(--verde-claro));
        color: white;
        border: none;
        border-radius: 30px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        font-size: 1rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 8px 25px rgba(1, 133, 72, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 12px 35px rgba(1, 133, 72, 0.4);
        background: linear-gradient(45deg, var(--verde-claro), var(--verde-bolivar));
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) scale(0.98);
        animation: pulse 0.3s ease;
    }
    
    /* Botón primario con amarillo dorado */
    .stButton > button[kind="primary"] {
        background: linear-gradient(45deg, var(--amarillo-dorado), var(--amarillo-claro));
        color: var(--verde-oscuro);
        font-weight: 700;
        box-shadow: 0 8px 25px rgba(244, 181, 26, 0.4);
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(45deg, var(--amarillo-claro), var(--amarillo-dorado));
        box-shadow: 0 12px 35px rgba(244, 181, 26, 0.5);
        color: var(--verde-bolivar);
    }
    
    /* Métricas con colores corporativos */
    .metric-container, [data-testid="metric-container"] {
        background: linear-gradient(135deg, var(--verde-bolivar), var(--verde-claro));
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 8px 20px rgba(1, 133, 72, 0.3);
        transition: all 0.3s ease;
        border: 2px solid var(--amarillo-dorado);
    }
    
    .metric-container:hover, [data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(1, 133, 72, 0.4);
    }
    
    /* Alertas con colores corporativos */
    .stAlert {
        border-radius: 15px;
        border-left: 6px solid;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
        animation: slideInUp 0.5s ease-out;
    }
    
    /* Alerta de éxito - Verde Bolívar */
    .stSuccess, [data-testid="success"] {
        background: linear-gradient(90deg, var(--verde-bolivar), var(--verde-claro));
        color: white;
        border-left-color: var(--amarillo-dorado);
    }
    
    /* Alerta de error */
    .stError, [data-testid="error"] {
        background: linear-gradient(90deg, #dc3545, #c82333);
        color: white;
        border-left-color: var(--amarillo-dorado);
    }
    
    /* Alerta de advertencia - Amarillo dorado */
    .stWarning, [data-testid="warning"] {
        background: linear-gradient(90deg, var(--amarillo-dorado), var(--amarillo-claro));
        color: var(--verde-oscuro);
        border-left-color: var(--verde-bolivar);
        font-weight: 600;
    }
    
    /* Alerta de información */
    .stInfo, [data-testid="info"] {
        background: linear-gradient(90deg, #17a2b8, #138496);
        color: white;
        border-left-color: var(--amarillo-dorado);
    }
    
    /* Contenedor de carga de archivos */
    .uploadedFile, [data-testid="fileUploader"] {
        background: linear-gradient(135deg, rgba(1, 133, 72, 0.1), rgba(244, 181, 26, 0.1));
        border: 2px dashed var(--verde-bolivar);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .uploadedFile:hover, [data-testid="fileUploader"]:hover {
        border-color: var(--amarillo-dorado);
        background: linear-gradient(135deg, rgba(1, 133, 72, 0.15), rgba(244, 181, 26, 0.15));
        transform: scale(1.02);
    }
    
    /* Spinner con colores corporativos */
    .stSpinner > div {
        border-top-color: var(--verde-bolivar) !important;
        border-right-color: var(--amarillo-dorado) !important;
    }
    
    /* Sidebar elementos mejorados */
    .css-1d391kg .stMarkdown, [data-testid="stSidebar"] .stMarkdown {
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 400;
    }
    
    /* Títulos del sidebar */
    .css-1d391kg h2, [data-testid="stSidebar"] h2 {
        color: var(--amarillo-dorado) !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        border-bottom: 2px solid rgba(244, 181, 26, 0.5);
        padding-bottom: 8px;
    }
    
    .css-1d391kg h3, [data-testid="stSidebar"] h3 {
        color: var(--amarillo-dorado) !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin: 1.5rem 0 0.8rem 0 !important;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* CUADRO DE INFORMACIÓN - SELECTORES EXHAUSTIVOS PARA FONDO BLANCO */
    
    /* Selectores principales para st.info en sidebar */
    .css-1d391kg .stInfo,
    [data-testid="stSidebar"] .stInfo,
    [data-testid="stSidebar"] [data-testid="stInfo"],
    .css-1d391kg [data-baseweb="notification"],
    [data-testid="stSidebar"] [data-baseweb="notification"],
    .css-1d391kg .element-container .stInfo,
    [data-testid="stSidebar"] .element-container .stInfo,
    .sidebar .stInfo,
    div[data-testid="stSidebar"] div[data-testid="stInfo"],
    div[data-testid="stSidebar"] div[data-baseweb="notification"] {
        background-color: white !important;
        background: white !important;
        border: 3px solid var(--amarillo-dorado) !important;
        border-radius: 15px !important;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.2),
            0 4px 16px rgba(244, 181, 26, 0.3) !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        transition: all 0.3s ease !important;
    }
    
    /* Hover effects para todos los selectores */
    .css-1d391kg .stInfo:hover,
    [data-testid="stSidebar"] .stInfo:hover,
    [data-testid="stSidebar"] [data-testid="stInfo"]:hover,
    .css-1d391kg [data-baseweb="notification"]:hover,
    [data-testid="stSidebar"] [data-baseweb="notification"]:hover,
    .css-1d391kg .element-container .stInfo:hover,
    [data-testid="stSidebar"] .element-container .stInfo:hover,
    .sidebar .stInfo:hover,
    div[data-testid="stSidebar"] div[data-testid="stInfo"]:hover,
    div[data-testid="stSidebar"] div[data-baseweb="notification"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.25),
            0 6px 20px rgba(244, 181, 26, 0.4) !important;
        border-color: var(--amarillo-claro) !important;
        background-color: rgba(255, 255, 255, 0.98) !important;
        background: rgba(255, 255, 255, 0.98) !important;
    }
    
    /* Texto dentro del cuadro - selectores exhaustivos */
    .css-1d391kg .stInfo div,
    [data-testid="stSidebar"] .stInfo div,
    [data-testid="stSidebar"] [data-testid="stInfo"] div,
    .css-1d391kg [data-baseweb="notification"] div,
    [data-testid="stSidebar"] [data-baseweb="notification"] div,
    .css-1d391kg .element-container .stInfo div,
    [data-testid="stSidebar"] .element-container .stInfo div,
    .sidebar .stInfo div,
    div[data-testid="stSidebar"] div[data-testid="stInfo"] div,
    div[data-testid="stSidebar"] div[data-baseweb="notification"] div,
    .css-1d391kg .stInfo p,
    [data-testid="stSidebar"] .stInfo p,
    .css-1d391kg .stInfo span,
    [data-testid="stSidebar"] .stInfo span {
        color: var(--verde-oscuro) !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.6 !important;
        font-size: 0.9rem !important;
    }
    
    /* Estilos para listas en el sidebar - selectores exhaustivos */
    .css-1d391kg .stInfo ul,
    [data-testid="stSidebar"] .stInfo ul,
    [data-testid="stSidebar"] [data-testid="stInfo"] ul,
    .css-1d391kg [data-baseweb="notification"] ul,
    [data-testid="stSidebar"] [data-baseweb="notification"] ul,
    div[data-testid="stSidebar"] div[data-testid="stInfo"] ul,
    div[data-testid="stSidebar"] div[data-baseweb="notification"] ul {
        margin: 0.5rem 0 !important;
        padding-left: 1rem !important;
    }
    
    .css-1d391kg .stInfo li,
    [data-testid="stSidebar"] .stInfo li,
    [data-testid="stSidebar"] [data-testid="stInfo"] li,
    .css-1d391kg [data-baseweb="notification"] li,
    [data-testid="stSidebar"] [data-baseweb="notification"] li,
    div[data-testid="stSidebar"] div[data-testid="stInfo"] li,
    div[data-testid="stSidebar"] div[data-baseweb="notification"] li {
        margin: 0.5rem 0 !important;
        color: var(--verde-oscuro) !important;
        font-weight: 500 !important;
    }
    
    /* Texto en negrita en sidebar - selectores exhaustivos */
    .css-1d391kg .stInfo strong,
    [data-testid="stSidebar"] .stInfo strong,
    [data-testid="stSidebar"] [data-testid="stInfo"] strong,
    .css-1d391kg [data-baseweb="notification"] strong,
    [data-testid="stSidebar"] [data-baseweb="notification"] strong,
    div[data-testid="stSidebar"] div[data-testid="stInfo"] strong,
    div[data-testid="stSidebar"] div[data-baseweb="notification"] strong,
    .css-1d391kg .stInfo b,
    [data-testid="stSidebar"] .stInfo b,
    .css-1d391kg [data-baseweb="notification"] b,
    [data-testid="stSidebar"] [data-baseweb="notification"] b {
        color: var(--verde-bolivar) !important;
        font-weight: 700 !important;
        text-shadow: none !important;
    }
    
    /* Enlaces en el sidebar */
    .css-1d391kg a, [data-testid="stSidebar"] a {
        color: var(--amarillo-dorado) !important;
        text-decoration: none !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        padding: 0.5rem 0.8rem !important;
        border-radius: 8px !important;
        display: inline-block !important;
        background: rgba(244, 181, 26, 0.1) !important;
        border: 1px solid rgba(244, 181, 26, 0.3) !important;
    }
    
    .css-1d391kg a:hover, [data-testid="stSidebar"] a:hover {
        color: var(--verde-bolivar) !important;
        background: var(--amarillo-dorado) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(244, 181, 26, 0.4) !important;
    }
    
    /* Divisores en sidebar */
    .css-1d391kg hr, [data-testid="stSidebar"] hr {
        border: none !important;
        height: 2px !important;
        background: rgba(244, 181, 26, 0.6) !important;
        border-radius: 2px !important;
        margin: 1.5rem 0 !important;
    }
    
    /* Icono especial para el header de información */
    .css-1d391kg .stInfo::before, [data-testid="stSidebar"] .stInfo::before {
        content: "💡";
        position: absolute;
        top: -10px;
        right: 15px;
        font-size: 1.5rem;
        background: var(--verde-bolivar);
        border-radius: 50%;
        width: 35px;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid var(--amarillo-dorado);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* Efecto brillante para el cuadro de información */
    .css-1d391kg .stInfo, [data-testid="stSidebar"] .stInfo {
        position: relative;
        overflow: hidden;
    }
    
    .css-1d391kg .stInfo::after, [data-testid="stSidebar"] .stInfo::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(244, 181, 26, 0.2), transparent);
        transform: rotate(45deg);
        animation: shimmer 6s infinite;
    }
    
    /* SELECTORES DE RESPALDO UNIVERSALES - FUERZA MÁXIMA */
    
    /* Cualquier elemento info dentro del sidebar */
    [data-testid="stSidebar"] div[class*="info" i],
    [data-testid="stSidebar"] div[class*="Info" i],
    [data-testid="stSidebar"] div[class*="notification" i],
    [data-testid="stSidebar"] div[data-baseweb*="notification"],
    section[data-testid="stSidebar"] div[class*="info" i],
    section[data-testid="stSidebar"] div[class*="Info" i] {
        background-color: white !important;
        background: white !important;
        border: 3px solid #F4B51A !important;
        border-radius: 15px !important;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2) !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    /* Fuerza el color del texto */
    [data-testid="stSidebar"] div[class*="info" i] *,
    [data-testid="stSidebar"] div[class*="Info" i] *,
    [data-testid="stSidebar"] div[class*="notification" i] *,
    [data-testid="stSidebar"] div[data-baseweb*="notification"] * {
        color: #016639 !important;
    }
    
    /* Selectores adicionales por posición */
    [data-testid="stSidebar"] > div > div > div > div[data-stale="false"] {
        background: white !important;
        border: 3px solid #F4B51A !important;
        border-radius: 15px !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
    }
    
    /* Expansor personalizado */
    .streamlit-expanderHeader {
        background: linear-gradient(90deg, var(--verde-bolivar), var(--verde-claro));
        color: white;
        border-radius: 12px;
        font-weight: bold;
        font-family: 'Inter', sans-serif;
        border: 2px solid var(--amarillo-dorado);
        transition: all 0.3s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(90deg, var(--verde-claro), var(--verde-bolivar));
        transform: scale(1.02);
    }
    
    /* Divisores con gradiente corporativo */
    hr {
        border: none;
        height: 4px;
        background: linear-gradient(90deg, var(--verde-bolivar), var(--amarillo-dorado), var(--verde-bolivar));
        border-radius: 3px;
        margin: 2.5rem 0;
        animation: shimmer 3s infinite;
        background-size: 200% 100%;
    }
    
    /* Contenedor de JSON */
    .stJson {
        background: linear-gradient(135deg, var(--verde-oscuro), var(--verde-bolivar));
        border-radius: 15px;
        padding: 1.5rem;
        border: 2px solid var(--amarillo-dorado);
    }
    
    /* DISEÑO RESPONSIVO */
    
    /* Tablets */
    @media (max-width: 768px) {
        .block-container {
            margin: 0.5rem;
            padding: 1.5rem;
            border-radius: 15px;
        }
        
        h1 {
            font-size: 1.8rem;
        }
        
        .stButton > button {
            padding: 0.7rem 2rem;
            font-size: 0.9rem;
        }
        
        .metric-container, [data-testid="metric-container"] {
            padding: 1rem;
            margin: 0.3rem 0;
        }
    }
    
    /* Móviles */
    @media (max-width: 480px) {
        .block-container {
            margin: 0.25rem;
            padding: 1rem;
            border-radius: 12px;
        }
        
        h1 {
            font-size: 1.5rem;
        }
        
        h2, h3 {
            font-size: 1.2rem;
        }
        
        .stButton > button {
            padding: 0.6rem 1.5rem;
            font-size: 0.85rem;
            border-radius: 25px;
        }
        
        .metric-container, [data-testid="metric-container"] {
            padding: 0.8rem;
            margin: 0.2rem 0;
        }
        
        .uploadedFile, [data-testid="fileUploader"] {
            padding: 1rem;
        }
        
        .stAlert {
            padding: 0.8rem 1rem;
        }
    }
    
    /* Modo oscuro automático */
    @media (prefers-color-scheme: dark) {
        .block-container {
            background: rgba(52, 58, 64, 0.95);
            color: white;
        }
        
        h1, h2, h3 {
            color: var(--amarillo-dorado);
        }
    }
    
    /* Microinteracciones adicionales */
    .stSelectbox > div, .stTextInput > div, .stTextArea > div {
        transition: all 0.3s ease;
        border-radius: 10px;
    }
    
    .stSelectbox > div:hover, .stTextInput > div:hover, .stTextArea > div:hover {
        box-shadow: 0 4px 15px rgba(1, 133, 72, 0.2);
        transform: translateY(-1px);
    }
    
    /* Efecto de carga para toda la página */
    .main {
        animation: fadeIn 1.2s ease-in-out;
    }
    
    /* Logo animado */
    img {
        transition: all 0.3s ease;
        border-radius: 10px;
    }
    
    img:hover {
        transform: scale(1.05) rotate(2deg);
        box-shadow: 0 8px 25px rgba(1, 133, 72, 0.3);
    }
</style>
""", unsafe_allow_html=True)

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