"""Juror agent implementation for jury deliberation."""

import time
import random
from typing import List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseLanguageModel

from jury_simulation.state import JuryState
from config.llm_manager import llm_manager


class Juror:
    """Represents an individual jury member with their own personality and background."""
    
    def __init__(self, name: str, background: str, llm: BaseLanguageModel = None):
        """Initialize a juror.
        
        Args:
            name: Name of the juror
            background: Background description for the juror
            llm: Language model to use (defaults to global llm_manager)
        """
        self.name = name
        self.background = background
        self.llm = llm or llm_manager.get_llm()
    
    def create_response_function(self):
        """Create a response function for this juror that can be used in LangGraph.
        
        Returns:
            Function that takes JuryState and returns updated state
        """
        def juror_response(state: JuryState) -> dict:
            """Generate a response from this juror during deliberation.
            
            Args:
                state: Current jury deliberation state
                
            Returns:
                Dictionary with updated state containing the juror's message
            """
            if self.llm is None:
                message = AIMessage(
                    content="Cannot generate response - API key not configured", 
                    name=self.name
                )
                return {"messages": [message]}

            case = state["case_details"]
            current_round = state.get("current_round", 1)
            current_juror_index = state.get("current_juror_index", 0)

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

            # Static system prompt
            system_prompt = f"""You are {self.name}, a jury member with this background:
{self.background}

Case details: {case}

Role: Engage thoughtfully in deliberation, staying true to your personality."""

            user_prompt = f"""You are {self.name}, a jury member in Round {current_round} of deliberation.

Full deliberation so far:
{context}

As {self.name}, give your perspective on this case. Consider what others have said and build on the discussion. Keep it to 2-3 sentences and be conversational.

At the end of your response, indicate your current stance by adding:
[Current stance: GUILTY/NOT GUILTY] - [brief reason referencing the deliberation]"""

            # Add rate limiting and retry logic
            max_retries = 3
            base_delay = 5  # seconds
            
            for attempt in range(max_retries):
                try:
                    # Add a small delay between requests to avoid rate limiting
                    if attempt > 0:
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 2)
                        print(f"⏳ Rate limit hit for {self.name}, waiting {delay:.1f} seconds...")
                        time.sleep(delay)
                    else:
                        # Small delay even on first attempt
                        time.sleep(random.uniform(1, 3))
                    
                    messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt)
                    ]
                    response = self.llm.invoke(messages)
                    message = AIMessage(content=response.content, name=self.name)
                    break
                    
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "quota" in error_msg.lower():
                        if attempt < max_retries - 1:
                            continue  # Retry with longer delay
                        else:
                            print(f"❌ Rate limit exceeded for {self.name} after {max_retries} attempts")
                            message = AIMessage(
                                content=f"I need more time to consider this case due to system limitations.", 
                                name=self.name
                            )
                    else:
                        print(f"Error generating response for {self.name}: {e}")
                        message = AIMessage(
                            content=f"I need more time to consider this case.", 
                            name=self.name
                        )
                    break

            # Advance to next juror
            next_juror_index = current_juror_index + 1

            return {
                "messages": [message],
                "current_juror_index": next_juror_index
            }
        
        return juror_response

    def get_last_two_rounds_context(self, messages: List[BaseMessage], current_round: int) -> List[BaseMessage]:
        """Extract messages from the last two rounds of deliberation.
        
        Args:
            messages: All messages from the deliberation
            current_round: Current round number
            
        Returns:
            List of messages from the last two rounds
        """
        # Early return for initial rounds
        if current_round <= 2 or len(messages) <= 6:  # Fallback to at least 6 messages
            return messages

        # Track round transitions
        round_transitions = {}

        for i, msg in enumerate(messages):
            if hasattr(msg, 'name') and msg.name == "Moderator":
                if "=== DELIBERATION ROUND" in msg.content:
                    try:
                        # Extract round number
                        round_str = msg.content.split("ROUND ")[1].split(" ===")[0]
                        round_num = int(round_str)
                        round_transitions[round_num] = i
                    except (IndexError, ValueError):
                        continue

        # Determine starting index
        if current_round == 1:
            # Include all messages
            start_idx = 0
        elif current_round == 2:
            # Include from round 1 onwards
            start_idx = round_transitions.get(1, 0)
        else:
            # Include from two rounds ago
            two_rounds_ago = current_round - 1
            start_idx = round_transitions.get(two_rounds_ago, 0)

            # Fallback: if we can't find the round marker, use last N messages
            if start_idx == 0 and len(messages) > 12:
                # Estimate ~4-6 messages per round, so ~12 for 2 rounds
                start_idx = len(messages) - 12

        return messages[start_idx:]
