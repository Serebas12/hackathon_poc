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
from react_agent.state import CustomState

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

@tool("cedula_tool", description="Una función que retorna un número de cédula")
async def cedula_tool() -> str:
    """
    Una función que retorna un número de cédula fijo.
    
    Returns:
        str: Retorna un número de cédula predefinido
    """
    return "el número de cedula es 1032323323"

@tool("registraduria_tool", description="Una función que consulta el estado de una persona en la registraduría.")
async def registraduria_tool() -> str:
    """
    Una función que consulta el estado de una persona en la registraduría.
    
    Returns:
        str: Retorna el estado de la persona
    """
    return "fallecido"

@tool("fecha_defuncion_tool", description="Una función que retorna la fecha de defunción.")
async def fecha_defuncion_tool() -> str:
    """
    Una función que retorna la fecha de defunción.
    
    Returns:
        str: Retorna una fecha de defunción predefinida
    """
    return "12 de enero de 2025"


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
