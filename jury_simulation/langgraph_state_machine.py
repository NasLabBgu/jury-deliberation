"""LangGraph state machine for jury deliberation workflow."""

from typing import Dict, List, Tuple
from langgraph.graph import StateGraph, START, END

from jury_simulation.state import JuryState
from agents.juror import Juror
from agents.moderator import Moderator
from agents.verdict_manager import VerdictManager
from config.data_loader import load_backgrounds_from_yaml, load_backgrounds_from_files


class LangGraphStateMachine:
    """LangGraph-based state machine for jury deliberation."""
    
    def __init__(self):
        """Initialize the state machine."""
        self.graph = None
        self.jury_backgrounds: Dict[str, str] = {}
        self.total_rounds = 3
        self.moderator = Moderator()
        self.verdict_manager = VerdictManager()
    
    def create_jury_graph(
        self, 
        yaml_file: str = None, 
        background_files: List[str] = None, 
        total_rounds: int = 3
    ) -> Tuple[StateGraph, Dict[str, str], int]:
        """Create the jury deliberation graph.

        Args:
            yaml_file: Path to YAML file with jury member data
            background_files: List of text files (for backward compatibility)
            total_rounds: Number of deliberation rounds before final verdict

        Returns:
            Tuple of (compiled_graph, backgrounds, total_rounds)
        """
        # Load backgrounds - prioritize YAML file if provided
        if yaml_file:
            backgrounds = load_backgrounds_from_yaml(yaml_file)
        elif background_files:
            # Fallback backgrounds for file-based loading
            fallback_backgrounds = {
                "Alice": "Retired teacher, 30 years experience. Values fairness and second chances.",
                "Bob": "Small business owner. Practical, fact-focused, believes in personal responsibility.",
                "Carol": "Social worker with family court experience. Empathetic, considers circumstances.",
                "David": "Engineer with technical background. Data-driven, prefers clear evidence."
            }
            backgrounds = load_backgrounds_from_files(background_files, fallback_backgrounds)
        else:
            # Default backgrounds
            backgrounds = {
                "Alice": "Retired teacher, 30 years experience. Values fairness and second chances.",
                "Bob": "Small business owner. Practical, fact-focused, believes in personal responsibility.",
                "Carol": "Social worker with family court experience. Empathetic, considers circumstances.",
                "David": "Engineer with technical background. Data-driven, prefers clear evidence."
            }

        self.jury_backgrounds = backgrounds
        self.total_rounds = total_rounds

        # Create the workflow
        workflow = StateGraph(JuryState)

        # Add moderator, start_round, and final verdict nodes
        workflow.add_node("moderator", self.moderator.moderate)
        workflow.add_node("start_round", self.moderator.start_round)
        workflow.add_node("final_verdict", self.verdict_manager.collect_final_verdicts)

        # Create and add jury member nodes
        juror_agents = {}
        for jury_name in backgrounds.keys():
            juror = Juror(jury_name, backgrounds[jury_name])
            juror_agents[jury_name] = juror
            workflow.add_node(jury_name, juror.create_response_function())

        # Set up flow
        workflow.add_edge(START, "moderator")
        workflow.add_conditional_edges("moderator", self.moderator.should_continue)

        # start_round determines what happens next
        workflow.add_conditional_edges("start_round", self.moderator.should_continue)

        # Each jury member goes back to flow control
        for jury_name in backgrounds.keys():
            workflow.add_conditional_edges(jury_name, self.moderator.should_continue)

        # Final verdict goes to END
        workflow.add_edge("final_verdict", END)

        # Compile the graph
        self.graph = workflow.compile()
        
        return self.graph, backgrounds, total_rounds
    
    def get_graph(self) -> StateGraph:
        """Get the compiled graph.
        
        Returns:
            The compiled LangGraph state machine
        """
        return self.graph
    
    def get_jury_backgrounds(self) -> Dict[str, str]:
        """Get the current jury backgrounds.
        
        Returns:
            Dictionary mapping jury names to their backgrounds
        """
        return self.jury_backgrounds
    
    def get_total_rounds(self) -> int:
        """Get the total number of deliberation rounds.
        
        Returns:
            Number of deliberation rounds
        """
        return self.total_rounds
    
    def set_total_rounds(self, rounds: int):
        """Set the number of deliberation rounds.
        
        Args:
            rounds: Number of deliberation rounds
        """
        self.total_rounds = rounds
