"""Moderator agent for managing jury deliberation rounds."""

from langchain_core.messages import AIMessage
from jury_simulation.state import JuryState


class Moderator:
    """Moderator agent that manages the flow of jury deliberation rounds."""
    
    def __init__(self):
        """Initialize the moderator."""
        pass
    
    def moderate(self, state: JuryState) -> dict:
        """Enhanced moderator to manage multi-round deliberations.
        
        Args:
            state: Current jury deliberation state
            
        Returns:
            Dictionary with updated state
        """
        current_round = state.get("current_round", 0)
        current_juror_index = state.get("current_juror_index", 0)

        # Only announce the very beginning of deliberation
        if current_round == 0 and current_juror_index == 0:
            msg = AIMessage(content="=== JURY DELIBERATION BEGINS ===", name="Moderator")
            return {
                "messages": [msg],
                "current_round": current_round,
                "current_juror_index": current_juror_index
            }

        # For all other cases, just pass through without messages
        return {
            "current_round": current_round,
            "current_juror_index": current_juror_index
        }
    
    def start_round(self, state: JuryState) -> dict:
        """Start a new round of deliberation.
        
        Args:
            state: Current jury deliberation state
            
        Returns:
            Dictionary with updated state
        """
        current_round = state.get("current_round", 0) + 1
        total_rounds = state.get("total_rounds", 3)
        jury_order = state.get("jury_order", [])

        # If we've completed all rounds, signal for final verdict
        if current_round > total_rounds:
            msg = AIMessage(content="=== COLLECTING FINAL VERDICTS ===", name="Moderator")
            return {
                "messages": [msg],
                "current_round": current_round,
                "current_juror_index": 0
            }

        # Announce the new round
        msg = AIMessage(content=f"=== DELIBERATION ROUND {current_round} ===", name="Moderator")

        # Start new round with first juror
        return {
            "messages": [msg],
            "current_round": current_round,
            "current_juror_index": 0
        }
    
    def should_continue(self, state: JuryState) -> str:
        """Enhanced flow control for multi-round deliberations.
        
        Args:
            state: Current jury deliberation state
            
        Returns:
            String indicating the next action to take
        """
        current_round = state.get("current_round", 0)
        current_juror_index = state.get("current_juror_index", 0)
        total_rounds = state.get("total_rounds", 3)
        jury_order = state.get("jury_order", [])

        # If no jury order set, we're in trouble
        if not jury_order:
            return "final_verdict"

        # If we've completed all rounds, go to final verdict
        if current_round > total_rounds:
            return "final_verdict"

        # If this is the start (round 0), begin first round
        if current_round == 0:
            return "start_round"

        # If we're in a valid round, determine next action
        if current_juror_index < len(jury_order):
            # Next juror should speak
            return jury_order[current_juror_index]
        else:
            # All jurors have spoken in this round, start next round
            return "start_round"
