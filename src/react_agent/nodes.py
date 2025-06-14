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
from react_agent.tools import web_search

load_dotenv()  # Esto carga las variables del archivo .env

project_id = os.getenv("PROJECT_ID")

# Carga del modelo de GCP
llm_gcp=VertexAILLM(project=project_id).get_model()

#Creación de las tools 

def create_handoff_tool(agent_name: str):
    @tool(f"transfer_to_{agent_name}", description=f"Transferir al agente {agent_name}")
    def handoff(
        state: Annotated[CustomState, InjectedState],
        tool_call_id: Annotated[str, InjectedToolCallId]
    ) -> Command:
        # Creamos un mensaje de transferencia
        tool_msg = {
            "role": "tool",
            "content": f"Transferido a {agent_name}",
            "name": f"transfer_to_{agent_name}",
            "tool_call_id": tool_call_id,
        }
        return Command(
            goto=agent_name,
            update={"messages": state["messages"] + [tool_msg]},
            graph=Command.PARENT
        )
    return handoff

transfer_to_cedula = create_handoff_tool("cedula_agent")
transfer_to_registraduria = create_handoff_tool("registraduria_agent")
transfer_to_defuncion = create_handoff_tool("defuncion_agent")

#creación de los agentes react 

cedula_agent = create_react_agent(
    model=llm_gcp,
    tools=[web_search],
    prompt=(
        "You are a research agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, DO NOT do any math\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="cedula_agent",
)

registraduria_agent = create_react_agent(
    model=llm_gcp,
    tools=[web_search],
    prompt=(
        "You are a research agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, DO NOT do any math\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="registraduria_agent",
)

defuncion_agent = create_react_agent(
    model=llm_gcp,
    tools=[web_search],
    prompt=(
        "You are a research agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, DO NOT do any math\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="defuncion_agent",
)

# Creación del supervisor

supervisor_agent = create_react_agent(
    model=llm_gcp,
    tools=[transfer_to_cedula, transfer_to_registraduria, transfer_to_defuncion],
    prompt=(
        "You are a supervisor managing two agents:\n"
        "- Assign research to research_agent\n"
        "- Assign math to math_agent\n"
        "Only one agent at a time. No hagas trabajo tú mismo."
    ),
    name="supervisor"
)