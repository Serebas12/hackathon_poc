"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from typing import Any, Callable, List, Optional, cast

from langchain_tavily import TavilySearch  # type: ignore[import-not-found]

from react_agent.configuration import Configuration
from langchain_core.tools import tool
from typing import Annotated
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from langchain_core.tools import InjectedToolCallId
from react_agent.state import State

async def search(query: str) -> Optional[dict[str, Any]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    configuration = Configuration.from_context()
    wrapped = TavilySearch(max_results=configuration.max_search_results)
    return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))

@tool("web_search", description="Una función de búsqueda simple que retorna un string fijo.")
async def web_search(query: str) -> str:
    """
    Una función de búsqueda simple que retorna un string fijo.
    
    Args:
        query: El texto de búsqueda
        
    Returns:
        str: Retorna siempre "probando"
    """
    return "probando"

@tool("consulta_cedula_playwright", description="Consulta el estado vital de una persona en la Registraduría Nacional usando su número de cédula.")
async def consulta_cedula_playwright(cedula: str) -> str:
    """
    Consulta el estado vital de una persona en la página de defunciones de la Registraduría Nacional.
    
    Args:
        cedula: Número de cédula de ciudadanía a consultar (máximo 10 dígitos)
        
    Returns:
        str: Resultado de la consulta con el estado de la cédula (Vigente/Vivo o Fallecido)
    """
    import asyncio
    from playwright.async_api import async_playwright
    import os
    from datetime import datetime
    
    async def run_playwright_consultation():
        async with async_playwright() as p:
            try:
                # Crear enlace simbólico si no existe (para WSL/Linux)
                firefox_cache_dir = os.path.expanduser("~/.cache/ms-playwright")
                firefox_1482_path = os.path.join(firefox_cache_dir, "firefox-1482")
                firefox_1487_path = os.path.join(firefox_cache_dir, "firefox-1487")
                
                if not os.path.exists(firefox_1482_path) and os.path.exists(firefox_1487_path):
                    os.symlink(firefox_1487_path, firefox_1482_path)
                
                # Lanzar navegador
                browser = await p.firefox.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navegar a la página de defunciones
                await page.goto("https://defunciones.registraduria.gov.co/", timeout=30000)
                await page.wait_for_load_state("networkidle")
                
                # Esperar a que aparezca el campo de cédula
                await page.wait_for_selector("#nuip", timeout=10000)
                
                # Limpiar y llenar el campo de cédula
                await page.fill("#nuip", "")
                await page.fill("#nuip", str(cedula))
                
                # Hacer clic en el botón buscar
                await page.click("button.btn.btn-primary")
                
                # Esperar a que aparezca el resultado (puede ser exitoso o de error)
                try:
                    await page.wait_for_timeout(3000)  # Esperar 3 segundos para que cargue
                    
                    # Obtener todo el texto visible de la página
                    page_text = await page.inner_text("body")
                    
                                         # Verificar si hay un resultado válido
                    if "se encuentra en el archivo nacional" in page_text:
                        # Extraer información específica
                        if "Vigente (Vivo)" in page_text:
                            estado = "Vigente (Vivo)"
                        elif ("Fallecido" in page_text or 
                              "fallecid" in page_text.lower() or 
                              "Cancelada por Muerte" in page_text or
                              "cancelada por muerte" in page_text.lower()):
                            estado = "Fallecido"
                        else:
                            estado = "Estado no determinado"
                        
                        # Extraer fecha de consulta si está disponible
                        fecha_consulta = datetime.now().strftime("%d/%m/%Y")
                        if "Fecha Consulta:" in page_text:
                            lines = page_text.split('\n')
                            for line in lines:
                                if "Fecha Consulta:" in line:
                                    fecha_consulta = line.replace("Fecha Consulta:", "").strip()
                                    break
                        
                        result = f"""
Consulta de Cédula Exitosa
========================
Número de documento: {cedula}
Estado: {estado}
Fecha de consulta: {fecha_consulta}
Fuente: Registraduría Nacional del Estado Civil

La cédula {cedula} se encuentra en el archivo nacional de identificación con estado: {estado}
"""
                    
                    elif ("Cancelada por Muerte" in page_text or 
                          "cancelada por muerte" in page_text.lower()):
                        # Caso especial: Cédula cancelada por muerte
                        fecha_consulta = datetime.now().strftime("%d/%m/%Y")
                        if "Fecha Consulta:" in page_text:
                            lines = page_text.split('\n')
                            for line in lines:
                                if "Fecha Consulta:" in line:
                                    fecha_consulta = line.replace("Fecha Consulta:", "").strip()
                                    break
                        
                        result = f"""
Consulta de Cédula Exitosa
========================
Número de documento: {cedula}
Estado: Fallecido
Motivo: Cancelada por Muerte
Fecha de consulta: {fecha_consulta}
Fuente: Registraduría Nacional del Estado Civil

La cédula {cedula} está cancelada por muerte, por lo tanto el estado es: Fallecido
"""
                    
                    elif "no se encuentra" in page_text.lower() or "no existe" in page_text.lower():
                        result = f"""
Consulta de Cédula - No Encontrada
=================================
Número de documento: {cedula}
Estado: No encontrado en el archivo nacional
Fecha de consulta: {datetime.now().strftime("%d/%m/%Y")}

La cédula {cedula} no se encuentra registrada en el archivo nacional de identificación.
"""
                    
                    else:
                        result = f"""
Consulta de Cédula - Resultado Incierto
======================================
Número de documento: {cedula}
Fecha de consulta: {datetime.now().strftime("%d/%m/%Y")}

No se pudo determinar el estado de la cédula. Respuesta del sistema:
{page_text[:500]}...
"""
                
                except Exception as e:
                    result = f"Error durante la consulta de la cédula {cedula}: {str(e)}"
                
                await browser.close()
                return result
                
            except Exception as e:
                if 'browser' in locals():
                    await browser.close()
                return f"Error al consultar la cédula {cedula}: {str(e)}"
    
    return await run_playwright_consultation()

# @tool("cedula_tool", description="Una función que retorna un número de cédula")
# async def cedula_tool() -> str:
#     """
#     Una función que retorna un número de cédula fijo.
    
#     Returns:
#         str: Retorna un número de cédula predefinido
#     """
#     return "el número de cedula es 1032323323"


from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
import asyncio

import asyncio

@tool("cedula_tool", description="Una función que retorna un número de cédula")
async def cedula_tool(state: Annotated[State, InjectedState]) -> str:
    import fitz  # PyMuPDF
    import base64
    from PIL import Image
    import io
    from react_agent.file_manager import file_manager

    def process_pdf():
        # Intentar obtener archivo de la sesión
        session_id = getattr(state, 'session_id', None)
        cedula_path = None
        
        if session_id:
            cedula_path = file_manager.get_file_path(session_id, "cedula")
        
        # Fallback a archivo por defecto si no hay sesión o archivo
        if not cedula_path:
            cedula_path = "/home/jssaa/proyectos/react-agent/src/doc_pruebas/Cedula_seb.pdf"
        
        pdf_document = fitz.open(cedula_path)
        page = pdf_document[0]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        imag_cedula = base64.b64encode(buffer.getvalue()).decode()
        pdf_document.close()
        return imag_cedula

    imag_cedula = await asyncio.to_thread(process_pdf)

    # El resto de tu código (prompt, modelo, etc.) también puede tener partes bloqueantes.
    # Si usas model.invoke (que es síncrono), también debes envolverlo:
    from langchain_google_vertexai import ChatVertexAI
    from langchain_core.messages import HumanMessage

    prompt = """
    Contexto:
    Eres un modelo de IA multimodal especializado en extraer el número de cédula de una imagen.
    Instrucciones:
    1. Analiza la imagen y extrae el número de cédula.
    2. Devuelve el número de cédula.
    Formato de salida:
    Devuelve un único string que contenga el número de cédula.
    """

    model = ChatVertexAI(
        model_name="gemini-2.5-flash-preview-04-17",
        project="analitica-poc-gcp",
        location="us-central1",
        credentials_path="/home/jssaa/proyectos/react-agent/src/creds/credentials.json"
    )

    image_message = HumanMessage(
        content=[
            { "type": "text", "text": prompt },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{imag_cedula}"
                }
            }
        ]
    )

    # Si model.invoke es síncrono, también debes hacer esto:
    def call_model():
        return model.invoke([image_message])

    response = await asyncio.to_thread(call_model)

    # Si la respuesta es un objeto, extrae el texto:
    if hasattr(response, "content"):
        return response.content
    return str(f"El número de cédula es: {response}")



import httpx
from langchain.tools import tool
import os

@tool("registraduria_tool", description="Una función que consulta el estado de una persona en la registraduría.")

async def registraduria_tool(cedula: str) -> str:
    payload = {
        "url": "https://defunciones.registraduria.gov.co/",
        "actions": [
            {"type": "waitForSelector", "selector": "input#nuip"},
            {"type": "input", "selector": "input#nuip", "value": cedula},
            {"type": "click", "selector": "button"},
            {"type": "waitForSelector", "selector": "div.alert"}  # Ajusta si hay otro contenedor
        ],
        "output": {"format": "markdown"}
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.firecrawl.dev/v0/crawl",  # <-- endpoint corregido
            json=payload,
            headers={"Authorization": f"Bearer {os.environ['FIRECRAWL_API_KEY']}"}
        )
        response.raise_for_status()
        return response.text




# @tool("fecha_defuncion_tool", description="Una función que retorna la fecha de defunción.")
# async def fecha_defuncion_tool() -> str:
#     """
#     Una función que retorna la fecha de defunción.
    
#     Returns:
#         str: Retorna una fecha de defunción predefinida
#     """
#     return "12 de enero de 2025"


@tool("fecha_defuncion_tool", description="Una función que retorna la fecha de defunción.")
async def fecha_defuncion_tool(state: Annotated[State, InjectedState]) -> str:
    import fitz  # PyMuPDF
    import base64
    from PIL import Image
    import io
    from react_agent.file_manager import file_manager

    def process_pdf():
        # Intentar obtener archivo de la sesión
        session_id = getattr(state, 'session_id', None)
        defuncion_path = None
        
        if session_id:
            defuncion_path = file_manager.get_file_path(session_id, "defuncion")
        
        # Fallback a archivo por defecto si no hay sesión o archivo
        if not defuncion_path:
            defuncion_path = "/home/jssaa/proyectos/react-agent/src/doc_pruebas/CER_DEFUNCION.pdf"
        
        pdf_document = fitz.open(defuncion_path)
        page = pdf_document[0]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        imag_cedula = base64.b64encode(buffer.getvalue()).decode()
        pdf_document.close()
        return imag_cedula

    imag_cedula = await asyncio.to_thread(process_pdf)

    # El resto de tu código (prompt, modelo, etc.) también puede tener partes bloqueantes.
    # Si usas model.invoke (que es síncrono), también debes envolverlo:
    from langchain_google_vertexai import ChatVertexAI
    from langchain_core.messages import HumanMessage

    prompt = """
    # CONTEXTO
    Eres un sistema experto de IA especializado en la extracción de datos (OCR) de certificados oficiales de Colombia. Tu única tarea es identificar y extraer la "Fecha de la defunción".

    # INSTRUCCIONES CLAVE
    1.  **Enfócate en el título**: Busca en la imagen el texto exacto **"Fecha de la defunción"**.
    2.  **Extrae la fecha asociada**: Justo debajo o al lado de ese título, encontrarás los campos para "Año", "Mes" y "Día". Extrae los valores de esos campos específicos.
    3.  **IGNORA OTRAS FECHAS**: El documento contiene otras fechas, como la "Fecha de inscripción". Debes ignorar explícitamente todas las demás fechas y centrarte únicamente en la que está asociada a "Fecha de la defunción".
    4.  **Conversión del Mes**: El mes está escrito con tres letras (ej: 'DIC'). Conviértelo a su valor numérico de dos dígitos (ej: 'DIC' es '12', 'ENE' es '01').
    5.  **Validación**: El año debe ser un número de 4 dígitos.

    # FORMATO DE SALIDA
    Devuelve **únicamente** un string con la fecha en formato `AAAA-MM-DD`. No agregues texto, explicaciones ni ninguna otra palabra.

    Ejemplo de salida esperada:
    2023-12-10
    """

    model = ChatVertexAI(
        model_name="gemini-2.5-flash-preview-04-17",
        project="analitica-poc-gcp",
        location="us-central1",
        credentials_path="/home/jssaa/proyectos/react-agent/src/creds/credentials.json"
    )

    image_message = HumanMessage(
        content=[
            { "type": "text", "text": prompt },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{imag_cedula}"
                }
            }
        ]
    )

    # Si model.invoke es síncrono, también debes hacer esto:
    def call_model():
        return model.invoke([image_message])

    response = await asyncio.to_thread(call_model)

    # Si la respuesta es un objeto, extrae el texto:
    if hasattr(response, "content"):
        return response.content
    return str(f"La fecha de defunción es: {response}")

@tool("saldo_tool", description="Una función que consulta un producto del usuario, su saldo, fecha de desembolso y monto de desembolso.")
async def saldo_tool(cedula: str) -> str:
    """
    Una función que consulta el saldo de una persona usando su número de cédula.
    
    Args:
        cedula: El número de cédula de la persona
    
    Returns:
        str: Retorna el saldo, fecha y monto de desembolso, y nombre del producto
    """
    import pandas as pd
    import os
    from datetime import datetime
    
    def process_csv():
        """Función interna para procesar el CSV de forma síncrona"""
        # Ruta al archivo CSV
        csv_path = "/home/jssaa/proyectos/react-agent/src/doc_pruebas/data_saldos.csv"
        
        # Verificar si el archivo existe
        if not os.path.exists(csv_path):
            raise FileNotFoundError("No se pudo encontrar el archivo de datos de saldos")
        
        # Leer el archivo CSV
        df = pd.read_csv(csv_path)
        
        # Filtrar por número de cédula
        person_data = df[df['Cedula'].astype(str) == str(cedula)]
        
        if person_data.empty:
            raise ValueError(f"No se encontró información para la cédula {cedula}")
        
        # Obtener los datos de la primera fila (asumiendo una cédula por persona)
        row = person_data.iloc[0]
        
        saldo = row['Saldo']
        producto = row['Producto']
        fecha_desembolso = row['fecha desembolso']
        monto_desembolso = row['Mondo desembolso']  # Note: hay un typo en el CSV original
        
        return saldo, producto, fecha_desembolso, monto_desembolso
    
    try:
        # Ejecutar la operación bloqueante en un hilo separado
        saldo, producto, fecha_desembolso, monto_desembolso = await asyncio.to_thread(process_csv)
        
        # Formatear la fecha si es necesario (convertir de DD/MM/YYYY a formato legible)
        try:
            fecha_obj = datetime.strptime(fecha_desembolso, '%d/%m/%Y')
            fecha_formateada = fecha_obj.strftime('%d de %B de %Y')
            # Convertir mes en inglés a español
            meses = {
                'January': 'enero', 'February': 'febrero', 'March': 'marzo',
                'April': 'abril', 'May': 'mayo', 'June': 'junio',
                'July': 'julio', 'August': 'agosto', 'September': 'septiembre',
                'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
            }
            for ing, esp in meses.items():
                fecha_formateada = fecha_formateada.replace(ing, esp)
        except:
            fecha_formateada = fecha_desembolso  # Si no se puede formatear, usar original
        
        return f"el saldo de la persona es {saldo}, fecha de desembolso {fecha_formateada}, monto de desembolso {monto_desembolso} y nombre del producto {producto}"
        
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error al consultar la información: {str(e)}"


def create_handoff_tool(agent_name: str):
    @tool(f"transfer_to_{agent_name}", description=f"Transferir al agente {agent_name}")
    def handoff(
        state: Annotated[State, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> Command:
        from langchain_core.messages import ToolMessage

        # El goto debe ir al nombre completo del agente con _agent
        target_agent = f"{agent_name}_agent"
        
        tool_msg = ToolMessage(
            content=f"Transferido a {target_agent}",
            name=f"transfer_to_{agent_name}",
            tool_call_id=tool_call_id,
        )
        return Command(
            goto=target_agent,
            update={
                "messages": state.messages + [tool_msg],
                "session_id": getattr(state, 'session_id', None)  # Preservar session_id
            },
            graph=Command.PARENT
        )
    return handoff

transfer_to_cedula = create_handoff_tool("cedula")
transfer_to_registraduria = create_handoff_tool("registraduria")
transfer_to_defuncion = create_handoff_tool("defuncion")
transfer_to_saldo = create_handoff_tool("saldo")