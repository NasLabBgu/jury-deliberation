"""Data loading utilities for jury members and case files."""

import os
import yaml
import re
from typing import Dict, List, Optional, Tuple


def load_case_from_file(file_path: str, scenario_number: Optional[int] = None) -> str:
    """Load case details from text file.

    Args:
        file_path: Path to the case file
        scenario_number: If file contains multiple scenarios, specify which one (1, 2, 3, etc.)

    Returns:
        Case details as string

    Raises:
        FileNotFoundError: If the case file is not found
        ValueError: If the specified scenario number is not found
        Exception: For other file loading errors
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Check if file contains multiple scenarios
        if 'Scenario 1:' in content and 'Scenario 2:' in content:
            scenarios = {}

            # Split by scenario markers
            parts = content.split('Scenario ')
            for part in parts[1:]:  # Skip first empty part
                if ':' in part:
                    scenario_num = int(part.split(':')[0].strip())
                    scenario_text = 'Scenario ' + part
                    scenarios[scenario_num] = scenario_text.strip()

            if scenario_number:
                if scenario_number in scenarios:
                    return scenarios[scenario_number]
                else:
                    available = list(scenarios.keys())
                    raise ValueError(f"Scenario {scenario_number} not found. Available scenarios: {available}")
            else:
                # Return all scenarios combined
                return content
        else:
            # Single case file
            return content

    except FileNotFoundError:
        raise FileNotFoundError(f"Case file {file_path} not found")
    except Exception as e:
        raise Exception(f"Error loading case from {file_path}: {e}")


def list_scenarios_in_file(file_path: str) -> List[Tuple[int, str]]:
    """List available scenarios in a case file.

    Args:
        file_path: Path to the case file

    Returns:
        List of tuples containing (scenario_number, title_line)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        scenarios = []
        parts = content.split('Scenario ')
        for part in parts[1:]:
            if ':' in part:
                scenario_num = int(part.split(':')[0].strip())
                # Get first line after the colon as title
                title_line = part.split('\n')[0] if '\n' in part else part[:50]
                scenarios.append((scenario_num, title_line))

        return scenarios
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []


def load_backgrounds_from_yaml(file_path: str) -> Dict[str, str]:
    """Load jury backgrounds from YAML file supporting multiple structures.

    Args:
        file_path: Path to the YAML file

    Returns:
        Dictionary mapping jury member names to their background descriptions
    """
    backgrounds = {}

    try:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)

        for jury_key, jury_data in data.items():
            # Detect structure type by checking for key fields
            if 'first_name' in jury_data and 'last_name' in jury_data:
                # Detailed structure (like jurors.yaml)
                background = _process_detailed_structure(jury_data)
                full_name = f"{jury_data.get('first_name', 'Unknown')} {jury_data.get('last_name', 'Unknown')}"

            elif 'backstory' in jury_data:
                # Simplified structure (like agents.yaml, old_and_young.yaml)
                background = _process_simplified_structure(jury_data)
                full_name = _extract_name_from_backstory(jury_data.get('backstory', ''), jury_key)

            else:
                # Unknown structure - use available data
                background = _process_unknown_structure(jury_data)
                full_name = jury_key.replace('_', ' ').title()

            backgrounds[full_name] = background

    except FileNotFoundError:
        print(f"YAML file {file_path} not found, using empty backgrounds")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {file_path}: {e}")
        return {}
    except Exception as e:
        print(f"Error loading backgrounds from {file_path}: {e}")
        return {}

    return backgrounds


def _process_detailed_structure(jury_data: Dict) -> str:
    """Process detailed structure with separate fields for personal information."""
    biography = jury_data.get('biography', '')
    age = jury_data.get('age', 'Unknown age')
    education = jury_data.get('education', 'Unknown education')
    occupation = jury_data.get('occupation', 'Unknown occupation')
    income = jury_data.get('income', 'Unknown income')
    state = jury_data.get('state', 'Unknown state')
    religion = jury_data.get('religion', 'Unknown religion')
    race = jury_data.get('race', 'Unknown race')
    gender = jury_data.get('gender', 'Unknown gender')
    goal = jury_data.get('goal', 'Serve justice fairly')
    role = jury_data.get('role', 'Regular juror')

    # Combine all information into a comprehensive background
    background = f"{biography}\n\n"
    background += f"Personal Details: {age}, {gender}, {race}, {education}, {occupation} from {state}. "
    background += f"Income: {income}. Religion: {religion}.\n"
    background += f"Role: {role}\n"
    background += f"Goal: {goal}"

    return background


def _process_simplified_structure(jury_data: Dict) -> str:
    """Process simplified structure with backstory, role, and goal."""
    backstory = jury_data.get('backstory', '').strip()
    role = jury_data.get('role', '').strip()
    goal = jury_data.get('goal', '').strip()

    # Clean up multiline strings and remove template placeholders
    backstory = re.sub(r'\s+', ' ', backstory)
    role = re.sub(r'\s+', ' ', role)
    goal = re.sub(r'\s+', ' ', goal)

    # Remove template placeholders like {topic} and {current_year}
    backstory = re.sub(r'\{[^}]+\}', '[case topic]', backstory)
    role = re.sub(r'\{[^}]+\}', '[case topic]', role)
    goal = re.sub(r'\{[^}]+\}', '[case topic]', goal)

    background = f"{backstory}\n\n"
    if role and role != backstory:
        background += f"Role: {role}\n"
    if goal and goal != backstory:
        background += f"Goal: {goal}"

    return background.strip()


def _process_unknown_structure(jury_data: Dict) -> str:
    """Process unknown structure by using all available string data."""
    background_parts = []

    for key, value in jury_data.items():
        if isinstance(value, str) and value.strip():
            # Clean up multiline strings
            clean_value = re.sub(r'\s+', ' ', value.strip())
            background_parts.append(f"{key.replace('_', ' ').title()}: {clean_value}")

    return "\n".join(background_parts) if background_parts else "No background information available."


def _extract_name_from_backstory(backstory: str, fallback_key: str) -> str:
    """Extract a name from the backstory text, with fallback to jury key."""
    if not backstory:
        return fallback_key.replace('_', ' ').title()

    # Look for name patterns in the backstory
    # Pattern 1: "Name is a..." or "Name, a..."
    name_pattern1 = r'^([A-Z][a-z]+ [A-Z][a-z]+)\s+(?:is|,)'
    match1 = re.search(name_pattern1, backstory)
    if match1:
        return match1.group(1)

    # Pattern 2: Just first sentence that might contain a name
    name_pattern2 = r'^([A-Z][a-z]+ [A-Z][a-z]+)'
    match2 = re.search(name_pattern2, backstory)
    if match2:
        return match2.group(1)

    # Pattern 3: Look for any capitalized name in the first 50 characters
    name_pattern3 = r'([A-Z][a-z]+ [A-Z][a-z]+)'
    match3 = re.search(name_pattern3, backstory[:50])
    if match3:
        return match3.group(1)

    # Fallback to jury key
    return fallback_key.replace('_', ' ').title()


def load_backgrounds_from_files(file_paths: List[str], fallback_backgrounds: Dict[str, str]) -> Dict[str, str]:
    """Load jury backgrounds from text files (legacy function for backward compatibility).

    Args:
        file_paths: List of text file paths containing jury backgrounds
        fallback_backgrounds: Default backgrounds to use if files are not found

    Returns:
        Dictionary mapping jury member names to their background descriptions
    """
    backgrounds = {}
    jury_names = list(fallback_backgrounds.keys())

    for i, file_path in enumerate(file_paths):
        if i >= len(jury_names):
            break
        try:
            with open(file_path, 'r') as f:
                backgrounds[jury_names[i]] = f.read().strip()
        except FileNotFoundError:
            print(f"File {file_path} not found, using default background")
            backgrounds[jury_names[i]] = fallback_backgrounds[jury_names[i]]

    # Fill remaining with defaults
    for name in jury_names[len(file_paths):]:
        backgrounds[name] = fallback_backgrounds[name]

    return backgrounds
