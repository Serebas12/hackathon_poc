from langgraph.prebuilt import create_react_agent
from react_agent.chat_utils import  VertexAILLM, PromptLoader
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from dotenv import load_dotenv
from typing import Annotated
import os
from react_agent.state import State, ReactAgentState
from react_agent.tools import  cedula_tool, registraduria_tool, consulta_cedula_playwright, fecha_defuncion_tool, transfer_to_cedula, transfer_to_registraduria, transfer_to_defuncion, saldo_tool, transfer_to_saldo

load_dotenv()  # Esto carga las variables del archivo .env

project_id = os.getenv("PROJECT_ID")

# Carga del modelo de GCP
llm_gcp=VertexAILLM(project=project_id).get_model()

#creación de los agentes react 

cedula_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[cedula_tool],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
        "eres un experto que obtiene el número de documento de una persona.\n\n"
        "INSTRUCTIONS:\n"
        "- tu tarea es obtener el número de documento de la persona\n"
        "- no lo hagas tú mismo, usa la herramienta cedula_tool\n"
        "- si no tienes el número de documento, no lo hagas tú mismo, usa la herramienta cedula_tool\n"
        "- no pidas información adicional, solo llama la herramienta cedula_tool\n"
    ),
    name="cedula_agent",
)

registraduria_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[consulta_cedula_playwright],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
        "Eres un experto que consulta el estado vital de una persona en la Registraduría Nacional del Estado Civil.\n\n"
        "INSTRUCCIONES:\n"
        "- Tu tarea es verificar el estado de la persona (vivo/fallecido) usando el número de cédula\n"
        "- SIEMPRE usa la herramienta consulta_cedula_playwright con el número de cédula como parámetro\n"
        "- NO inventes información, solo usa los datos que obtienes de la herramienta\n"
        "- Si no tienes el número de cédula, solicita que se proporcione primero\n"
        "- La herramienta te dará información oficial de la Registraduría Nacional\n"
        "- Proporciona un resumen claro del estado encontrado (Vigente/Vivo, Fallecido, o No encontrado)\n"
    ),
    name="registraduria_agent",
)

defuncion_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[fecha_defuncion_tool],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
        "eres un experto que obtiene la fecha de defunción de una persona.\n\n"
        "INSTRUCTIONS:\n"
        "- tu tarea es obtener la fecha de defunción de la persona\n"
        "- no lo hagas tú mismo, usa la herramienta fecha_defuncion_tool\n"
        "- si no tienes la fecha de defunción, no lo hagas tú mismo, usa la herramienta fecha_defuncion_tool\n"
    ),
    name="defuncion_agent",
)

saldo_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[saldo_tool],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
    """
    Tu objetivo es determinar si una persona aplica o no a **Póliza Express** con base en los datos obtenidos mediante la herramienta `saldo_tool`.  

    ### Paso 1: Obtener número de cédula
    **ANTES de llamar saldo_tool**, debes buscar en el historial de conversación el número de cédula que fue extraído previamente por el cedula_agent. 
    - Busca en los mensajes anteriores respuestas que contengan números de cédula (generalmente números de 8-10 dígitos).
    - Una vez que identifiques el número de cédula, úsalo como parámetro para llamar `saldo_tool`.

    ### Paso 2: Llamar herramienta
    Debes consumir `saldo_tool(cedula="NUMERO_DE_CEDULA")` para obtener los siguientes datos:
    - Tipo de producto (ej. TARJETA DE CRÉDITO, CRÉDITO, Móvil Consumo Fijo, Móvil Consumo Libranza)
    - Saldo de la persona
    - Fecha de desembolso (formato YYYY-MM-DD)
    - Monto desembolsado

    ### Reglas duras a evaluar:

    **Regla 1:**  
    ✔ Aplica si el tipo de producto es **TARJETA DE CRÉDITO**  
    ✔ Y el **saldo es menor o igual a 200.000.000**

    **Regla 2:**  
    ✔ Aplica si el tipo de producto es **CRÉDITO**  
    ✔ Y el plan es uno de los siguientes:  
    - Móvil Consumo Fijo  
    - Móvil Consumo Libranza  
    - Móvil Vehículo Particular  
    ✔ Y la diferencia entre la **fecha de siniestro y la fecha de desembolso es mayor a 60 días**  
    ✔ Y el **monto desembolsado es menor a 50.000.000**

    **Regla 3:**  
    ✔ Aplica si el producto **no es TARJETA DE CRÉDITO ni uno de los planes válidos para crédito**  
    ✔ Y la diferencia entre la **fecha de siniestro y la fecha de desembolso es mayor a 730 días (2 años)**  
    ✔ Y el **saldo es menor a 50.000.000**

    **En todos los casos se debe cumplir adicionalmente lo siguiente:**
    - La **fecha de siniestro debe estar dentro de la vigencia del crédito** (inicio ≤ siniestro ≤ fin)
    - el estado de la persona en la registraduría debe ser fallecido.

    ### Instrucciones:
    1. Revisa el historial de mensajes para encontrar el número de cédula extraído previamente.
    2. Llama la herramienta `saldo_tool` con el número de cédula como parámetro.
    3. Evalúa si se cumple alguna de las reglas anteriores **junto con los dos requisitos obligatorios comunes**.
    4. Si **sí aplica**, genera una respuesta afirmando que aplica a Póliza Express, especificando **qué regla se cumplió y por qué**.
    5. Si **no aplica**, indica que no cumple con las condiciones para aplicar y menciona **cuál fue la razón más relevante del descarte**.

    ### Formato de salida:
    - Siempre responde en un solo bloque.
    - Empieza indicando si **Aplica a Póliza Express: Sí/No**
    - Luego justifica brevemente en lenguaje claro y profesional.
    """
    ),
    name="saldo_agent",
)

# Creación del supervisor

supervisor_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[transfer_to_cedula, transfer_to_registraduria],
    state_schema=ReactAgentState,  # Usar esquema compatible con react agent
    prompt=(
        """Eres un supervisor que coordina tres agentes especializados. Tu tarea es siempre ejecutar, en este orden y sin excepciones, las siguientes acciones:

        1. Obtener el número de documento del usuario usando la herramienta `cedula_tool`.
        2. Verificar el estado de la persona en la registraduría usando `registraduria_agent`, debes llamar la herramienta compartiendo el número de documento con el que se extrajo previamente.
        """
    ),
    name="supervisor"
)