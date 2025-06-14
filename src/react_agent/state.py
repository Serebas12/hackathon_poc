"""Define the state structures for the agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated, NotRequired

from typing import List, TypedDict
from langchain_core.messages import BaseMessage

class CustomState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

