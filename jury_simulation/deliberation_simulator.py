"""Main deliberation simulator that orchestrates the jury deliberation process."""

from typing import Optional
from langchain_core.messages import HumanMessage

from jury_simulation.langgraph_state_machine import LangGraphStateMachine
from jury_simulation.state import JuryState
from config.data_loader import load_case_from_file
from output.formatter import output_formatter


class DeliberationSimulator:
    """Main simulator that orchestrates jury deliberation sessions."""
    
    def __init__(self):
        """Initialize the deliberation simulator."""
        self.state_machine = LangGraphStateMachine()
        self.graph = None
        self.jury_backgrounds = {}
        self.total_rounds = 3
        self.current_case = None
        self.current_case_filename = None
        self.current_scenario_number = None
        self.current_jury_filename = None
    
    def load_jury_from_yaml(self, yaml_file_path: str, total_rounds: int = 3):
        """Load jury members from YAML file and initialize the graph.
        
        Args:
            yaml_file_path: Path to the YAML file containing jury member data
            total_rounds: Number of deliberation rounds
        """
        self.graph, self.jury_backgrounds, self.total_rounds = self.state_machine.create_jury_graph(
            yaml_file=yaml_file_path, 
            total_rounds=total_rounds
        )
        self.current_jury_filename = yaml_file_path
        
        print(f"Loaded jury members from {yaml_file_path}:")
        for name in self.jury_backgrounds.keys():
            print(f"  - {name}")
        print(f"Set to {total_rounds} deliberation rounds")
        print()
    
    def load_case_from_file(self, case_file_path: str, scenario_number: Optional[int] = None):
        """Load case details from a text file.
        
        Args:
            case_file_path: Path to the case file
            scenario_number: If file contains multiple scenarios, specify which one
        """
        try:
            self.current_case = load_case_from_file(case_file_path, scenario_number)
            self.current_case_filename = case_file_path
            self.current_scenario_number = scenario_number

            if scenario_number:
                print(f"✅ Loaded Scenario {scenario_number} from {case_file_path}")
            else:
                print(f"✅ Loaded case from {case_file_path}")

            # Show preview of the case
            preview = self.current_case[:200] + "..." if len(self.current_case) > 200 else self.current_case
            print(f"Case Preview: {preview}\n")

        except Exception as e:
            print(f"❌ Error loading case: {e}")
            raise
    
    def set_case_directly(self, case_details: str):
        """Set case details directly without loading from file.
        
        Args:
            case_details: The case details as a string
        """
        self.current_case = case_details
        self.current_case_filename = None
        self.current_scenario_number = None
    
    def set_deliberation_rounds(self, total_rounds: int):
        """Set the number of deliberation rounds.
        
        Args:
            total_rounds: Number of deliberation rounds
        """
        self.total_rounds = total_rounds
        if hasattr(self.state_machine, 'graph') and self.state_machine.graph:
            self.state_machine.set_total_rounds(total_rounds)
        print(f"Set deliberation to {total_rounds} rounds")
    
    def run_deliberation(self, case_input: Optional[str] = None, save_to_file: bool = True) -> Optional[str]:
        """Run a complete jury deliberation session.
        
        Args:
            case_input: Case details (if None, uses loaded case)
            save_to_file: Whether to save deliberation to markdown file
            
        Returns:
            Path to saved file if save_to_file is True, None otherwise
        """
        if self.graph is None:
            print("Cannot run deliberation - jury not loaded")
            return None

        # Use provided case or current loaded case
        if case_input is None:
            if self.current_case is None:
                print("No case provided and no case loaded from file")
                return None
            case_input = self.current_case
        else:
            # If case is provided directly, reset file tracking
            if case_input != self.current_case:
                self.current_case_filename = None
                self.current_scenario_number = None

        # Clear previous output and prepare for new deliberation
        output_formatter.clear_buffer()

        # Create jury order from backgrounds
        jury_order = list(self.jury_backgrounds.keys())
        juror_colors = output_formatter.assign_juror_colors(jury_order)

        # Calculate needed recursion limit dynamically
        jury_size = len(self.jury_backgrounds)
        # Formula: rounds × (start_round + all_jurors) + setup + final_verdict + safety_margin
        needed_steps = (self.total_rounds * (jury_size + 1)) + 5 + 5  # +5 setup, +5 safety
        recursion_limit = max(50, needed_steps)  # Minimum 50, or calculated amount
        print(f"📊 Jury size: {jury_size}, Rounds: {self.total_rounds}")
        print(f"🔄 Setting recursion limit to: {recursion_limit}")

        initial_state: JuryState = {
            "messages": [HumanMessage(content=case_input)],
            "case_details": case_input,
            "jury_backgrounds": self.jury_backgrounds,
            "current_round": 0,
            "current_juror_index": 0,
            "total_rounds": self.total_rounds,
            "jury_order": jury_order
        }

        # Process the deliberation with dynamic recursion limit
        config = {"recursion_limit": recursion_limit}
        for event in self.graph.stream(initial_state, config):
            for value in event.values():
                if "messages" in value and value["messages"]:
                    last_message = value["messages"][-1]
                    speaker = getattr(last_message, 'name', 'System')
                    content = last_message.content

                    # Print to console
                    print(f"{speaker}: {content}")
                    print()

                    # Format and store for markdown file
                    if save_to_file:
                        output_formatter.add_output(speaker, content)

        # Save to markdown file if requested
        if save_to_file:
            return output_formatter.save_deliberation_to_markdown(
                case_input, 
                filename=None,
                jury_filename=self.current_jury_filename,
                case_filename=self.current_case_filename,
                scenario_number=self.current_scenario_number,
                total_rounds=self.total_rounds
            )
        
        return None
    
    def get_status(self) -> dict:
        """Get current status of the simulator.
        
        Returns:
            Dictionary with current status information
        """
        return {
            "jury_loaded": self.graph is not None,
            "jury_members": list(self.jury_backgrounds.keys()) if self.jury_backgrounds else [],
            "jury_filename": self.current_jury_filename,
            "case_loaded": self.current_case is not None,
            "case_filename": self.current_case_filename,
            "scenario_number": self.current_scenario_number,
            "total_rounds": self.total_rounds,
            "case_preview": self.current_case[:200] + "..." if self.current_case and len(self.current_case) > 200 else self.current_case
        }
