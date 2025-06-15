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

    documento = state.Doc1

    print(f"[DEBUG] Estado recibido en cedula_tool: {state}")
    print(f"[DEBUG] Doc1 en cedula_tool: '{getattr(state, 'Doc1', None)}'")
   

    def process_pdf():
        pdf_document = fitz.open(f"/home/jssaa/proyectos/react-agent/src/doc_pruebas/{documento}.pdf")
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


@tool("registraduria_tool", description="Una función que consulta el estado de una persona en la registraduría.")
async def registraduria_tool() -> str:
    """
    Una función que consulta el estado de una persona en la registraduría.
    
    Returns:
        str: Retorna el estado de la persona
    """
    return "fallecido"


# @tool("fecha_defuncion_tool", description="Una función que retorna la fecha de defunción.")
# async def fecha_defuncion_tool() -> str:
#     """
#     Una función que retorna la fecha de defunción.
    
#     Returns:
#         str: Retorna una fecha de defunción predefinida
#     """
#     return "12 de enero de 2025"


@tool("fecha_defuncion_tool", description="Una función que retorna la fecha de defunción.")
async def fecha_defuncion_tool() -> str:
    import fitz  # PyMuPDF
    import base64
    from PIL import Image
    import io

    def process_pdf():
        pdf_document = fitz.open("/home/jssaa/proyectos/react-agent/src/doc_pruebas/CER_DEFUNCION.pdf")
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


def create_handoff_tool(agent_name: str):
    @tool(f"transfer_to_{agent_name}", description=f"Transferir al agente {agent_name}")
    def handoff(
        state: Annotated[State, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> Command:

        print(f"[DEBUG] Estado recibido en transfer_to_{agent_name}: {state}")
        print(f"[DEBUG] Doc1 en transfer_to_{agent_name}: '{getattr(state, 'Doc1', None)}'")

        tool_msg = {
            "role": "tool",
            "content": f"Transferido a {agent_name}",
            "name": f"transfer_to_{agent_name}",
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,
            update={"messages": state.messages + [tool_msg] , "Doc1": state.Doc1  },
            graph=Command.PARENT
        )
    return handoff

transfer_to_cedula = create_handoff_tool("cedula_agent")
transfer_to_registraduria = create_handoff_tool("registraduria_agent")
transfer_to_defuncion = create_handoff_tool("defuncion_agent")
