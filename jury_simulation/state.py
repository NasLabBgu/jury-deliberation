"""State definitions for jury deliberation simulation."""

from typing import TypedDict, Dict, List, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class JuryState(TypedDict):
    """State object for jury deliberation workflow.
    
    This defines the structure of the state that flows through the LangGraph
    workflow, containing all necessary information for jury deliberation.
    """
    messages: Annotated[List[BaseMessage], add_messages]
    case_details: str
    jury_backgrounds: Dict[str, str]
    current_round: int
    current_juror_index: int  # Track which juror is speaking within the round
    total_rounds: int  # Total number of deliberation rounds
    jury_order: List[str]  # Order of jury members
