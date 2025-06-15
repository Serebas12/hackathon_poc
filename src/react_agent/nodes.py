from langgraph.prebuilt import create_react_agent
from react_agent.chat_utils import  VertexAILLM, PromptLoader
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from dotenv import load_dotenv
from typing import Annotated
import os
from react_agent.state import State
from react_agent.tools import web_search, cedula_tool, registraduria_tool, fecha_defuncion_tool, transfer_to_cedula, transfer_to_registraduria, transfer_to_defuncion

load_dotenv()  # Esto carga las variables del archivo .env

project_id = os.getenv("PROJECT_ID")

# Carga del modelo de GCP
llm_gcp=VertexAILLM(project=project_id).get_model()

#creación de los agentes react 

cedula_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[cedula_tool],
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
    tools=[registraduria_tool],
    prompt=(
        "eres un experto que obtiene el estado de la persona en la registraduría.\n\n"
        "INSTRUCTIONS:\n"
        "- tu tarea es obtener el estado de la persona en la registraduría\n"
        "- no lo hagas tú mismo, usa la herramienta registraduria_tool\n"
        "- si no tienes el estado de la persona en la registraduría, no lo hagas tú mismo, usa la herramienta registraduria_tool\n"
    ),
    name="registraduria_agent",
)

defuncion_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[fecha_defuncion_tool],
    prompt=(
        "eres un experto que obtiene la fecha de defunción de una persona.\n\n"
        "INSTRUCTIONS:\n"
        "- tu tarea es obtener la fecha de defunción de la persona\n"
        "- no lo hagas tú mismo, usa la herramienta fecha_defuncion_tool\n"
        "- si no tienes la fecha de defunción, no lo hagas tú mismo, usa la herramienta fecha_defuncion_tool\n"
    ),
    name="defuncion_agent",
)

# Creación del supervisor

supervisor_agent = create_react_agent(
    model="azure_openai:gpt-4.1",
    tools=[transfer_to_cedula, transfer_to_registraduria, transfer_to_defuncion],
    prompt=(
        """Eres un supervisor que coordina tres agentes especializados. Tu tarea es siempre ejecutar, en este orden y sin excepciones, las siguientes acciones:

        1. Obtener el número de documento del usuario usando la herramienta `cedula_tool`.
        2. Verificar el estado de la persona en la registraduría usando `registraduria_agent`.
        3. Obtener la fecha de defunción usando `defuncion_agent`.

        ⚠️ Instrucciones clave (obligatorias):
        - Siempre debes iniciar ejecutando la herramienta `cedula_tool`. No preguntes, no confirmes, no hagas razonamientos antes de usarla.
        - No pidas ninguna información adicional al usuario. Toda la información requerida se obtiene únicamente con las herramientas.
        - Está prohibido iniciar una conversación o solicitar datos al usuario en este paso. Usa directamente `cedula_tool`.

        🔁 Repite siempre este flujo, sin desviarte ni invertir el orden de ejecución.

        Tu rol no es dialogar ni decidir: es coordinar a los agentes y ejecutar cada paso secuencialmente.
        """
    ),
    name="supervisor"
)