"""Verdict manager for collecting final verdicts from jury members."""

import time
import random
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel

from jury_simulation.state import JuryState
from config.llm_manager import llm_manager


class VerdictManager:
    """Manages the collection of final verdicts from all jury members."""
    
    def __init__(self, llm: BaseLanguageModel = None):
        """Initialize the verdict manager.
        
        Args:
            llm: Language model to use (defaults to global llm_manager)
        """
        self.llm = llm or llm_manager.get_llm()
    
    def collect_final_verdicts(self, state: JuryState) -> dict:
        """Collect final verdicts from all jury members.
        
        Args:
            state: Current jury deliberation state
            
        Returns:
            Dictionary with updated state containing final verdicts
        """
        if self.llm is None:
            summary = "=== FINAL VERDICTS ===\nCannot collect verdicts - API key not configured"
            return {"messages": [AIMessage(content=summary, name="Final_Verdict")]}

        case = state["case_details"]

        # Get FULL conversation history
        all_messages = state["messages"]
        deliberation_msgs = []
        for msg in all_messages:
            # Skip the initial case presentation (HumanMessage)
            if isinstance(msg, HumanMessage):
                continue
            # For AIMessages, check if they have a name attribute
            if isinstance(msg, AIMessage) and hasattr(msg, 'name'):
                # Skip "=== X ===" style moderator messages but include other moderator messages
                if msg.name == "Moderator" and "===" in msg.content:
                    continue
                # Include all other messages (juror deliberations and non-procedural moderator messages)
                deliberation_msgs.append(f"{msg.name}: {msg.content}")
        context = "\n".join(deliberation_msgs)

        # Get all jury members' final decisions
        verdicts = {}
        jury_names = list(state["jury_backgrounds"].keys())
        
        for i, jury_name in enumerate(jury_names):
            background = state["jury_backgrounds"][jury_name]

            # Static system prompt
            system_prompt = f"""You are {jury_name}, a jury member with this background:
{background}

Case details: {case}

Role: Engage thoughtfully in deliberation, staying true to your personality."""

            user_prompt = f"""You are {jury_name}, a jury member.

Full deliberation transcript:
{context}

After the full deliberation, what is your FINAL VERDICT?
Consider the arguments made during the discussion and explain how they influenced your decision.
Answer only: "GUILTY" or "NOT GUILTY" and give one sentence explaining why.

Format: VERDICT: [GUILTY/NOT GUILTY] - [brief reason referencing the deliberation]"""

            # Add rate limiting between verdict requests
            max_retries = 3
            base_delay = 4
            
            for attempt in range(max_retries):
                try:
                    # Progressive delay to avoid rate limits
                    if attempt > 0:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
                        print(f"⏳ Rate limit hit collecting verdict from {jury_name}, waiting {delay:.1f} seconds...")
                        time.sleep(delay)
                    else:
                        # Delay between jurors to avoid rapid requests
                        if i > 0:  # No delay for first juror
                            time.sleep(random.uniform(2, 4))

                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt)
                    ]
                    response = self.llm.invoke(messages)
                    verdict_line = response.content.strip()
                    break
                    
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "quota" in error_msg.lower():
                        if attempt < max_retries - 1:
                            continue  # Retry with longer delay
                        else:
                            print(f"❌ Rate limit exceeded collecting verdict from {jury_name}")
                            verdict_line = f"VERDICT: NOT GUILTY - Unable to determine due to system limitations"
                    else:
                        print(f"Error getting verdict from {jury_name}: {e}")
                        verdict_line = f"VERDICT: NOT GUILTY - Unable to determine due to technical issue"
                    break

            verdicts[jury_name] = verdict_line

        # Count votes
        guilty_votes = sum(1 for v in verdicts.values() if "GUILTY" in v.upper() and "NOT GUILTY" not in v.upper())
        not_guilty_votes = len(verdicts) - guilty_votes

        # Final summary
        summary = "=== FINAL VERDICTS ===\n"
        for jury_name, verdict in verdicts.items():
            summary += f"{jury_name}: {verdict}\n"

        summary += f"\nFINAL TALLY: {guilty_votes} Guilty, {not_guilty_votes} Not Guilty\n"

        if guilty_votes > not_guilty_votes:
            summary += "JURY DECISION: GUILTY"
        elif not_guilty_votes > guilty_votes:
            summary += "JURY DECISION: NOT GUILTY"
        else:
            summary += "JURY DECISION: HUNG JURY (TIE)"

        return {
            "messages": [AIMessage(content=summary, name="Final_Verdict")]
        }

    def get_deliberation_summary(self, messages: List[BaseMessage], max_messages: int = 25) -> str:
        """Create a summary of key discussion points from the deliberation.
        
        Args:
            messages: All messages from the deliberation
            max_messages: Maximum number of messages to include in summary
            
        Returns:
            String summary of the deliberation
        """
        # Filter out moderator announcements and get actual discussion
        discussion_messages = []
        for msg in messages:
            if hasattr(msg, 'name'):
                # Skip the initial case presentation
                if msg.name == "User":
                    continue
                discussion_messages.append(f"{msg.name}: {msg.content}")

        # Take the most recent discussion points
        if len(discussion_messages) > max_messages:
            discussion_messages = discussion_messages[-max_messages:]

        return "\n".join(discussion_messages)
