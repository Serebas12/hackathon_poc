"""Define a custom Reasoning and Action agent.

Works with a chat model with tool calling support.
"""

from datetime import UTC, datetime
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from react_agent.configuration import Configuration
from react_agent.state import  State, InputState
from react_agent.utils import load_chat_model
from react_agent.nodes import supervisor_agent, cedula_agent, registraduria_agent, defuncion_agent, saldo_agent


builder = StateGraph(State, input=InputState)


# Define the two nodes we will cycle between
builder.add_node("supervisor", supervisor_agent)
builder.add_node("cedula_agent", cedula_agent)
builder.add_node("registraduria_agent", registraduria_agent)
builder.add_node("defuncion_agent", defuncion_agent)
builder.add_node("saldo_agent", saldo_agent)

def supervisor_routing(state: State) -> str:
    """Determina a qué agente transferir según el tool_call del supervisor."""
    # Protección: verificar que existan mensajes

    if not state.messages:
        return "__end__"

    last = state.messages[-1]

    if not hasattr(last, "tool_calls") or not last.tool_calls:
        return "__end__"

    tool_call = last.tool_calls[0]  # Solo se espera una herramienta por llamada
    tool_name = tool_call.name

    if tool_name == "transfer_to_cedula":
        return "cedula_agent"
    elif tool_name == "transfer_to_registraduria":
        return "registraduria_agent"
    elif tool_name == "transfer_to_defuncion":
        return "defuncion_agent"
    elif tool_name == "transfer_to_saldo":
        return "saldo_agent"
    else:
        return "__end__"

# Set up the edges
builder.add_edge("__start__",  "supervisor")
builder.add_conditional_edges("supervisor", supervisor_routing)
builder.add_edge("cedula_agent", "supervisor")
builder.add_edge("registraduria_agent", "supervisor")
builder.add_edge("defuncion_agent", "supervisor")
builder.add_edge("saldo_agent", "supervisor")

# Compile the graph
graph = builder.compile()
