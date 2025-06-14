from langgraph.prebuilt import create_react_agent
from react_agent.chat_utils import  VertexAILLM, PromptLoader
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from dotenv import load_dotenv
from typing import Annotated
import os
from react_agent.state import CustomState
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
        "You are a supervisor managing three agents:\n"
        "- obtener  el número de documento de un usuario a cedula_agent\n"
        "- verificar el estado de la persona en la registraduría a registraduria_agent\n"
        "- obtener la fecha de defunción a defuncion_agent\n"
        "siempre tienes que obtener el número de documento de un usuario, verificar el estado de la persona en la registraduría y obtener la fecha de defunción, en ese orden sin excepciones"
        "para obtener el número de documento de un usuario, usa la herramienta cedula_tool y no pidas información adicional, no es requerido ningun otro dato"
    ),
    name="supervisor"
)