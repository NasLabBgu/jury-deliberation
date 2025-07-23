# LangGraph Jury Deliberation Simulation

A jury deliberation simulation system that uses Large Language Models (LLMs) to simulate realistic jury discussions and verdict decisions. 
The system is built using LangGraph, supporting multiple LLM providers.

## Overview

This project simulates jury deliberations by creating AI-powered jury members with distinct backgrounds and personalities. 
Each juror analyzes case evidence, participates in multi-round discussions, and ultimately votes on a verdict.

## Features

- **Multi-round deliberations**: Configure the number of discussion rounds before final verdict
- **Diverse jury personas**: Load jury members from YAML files with detailed backgrounds
- **Multiple case scenarios**: Support for various cases (including scenarios based of "My Cousin Vinny")
- **LLM flexibility**: Works with OpenAI GPT-4 or Google Gemini models
- **Structured output**: Saves deliberations as formatted markdown files with speaker colors
- **Configurable jury size**: Simulate deliberations with 2-12 jury members
- **Intermediate verdict tracking**: Each juror declares their current stance (GUILTY/NOT GUILTY) at the end of each deliberation round, allowing tracking of opinion evolution

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

### API Keys

The system supports two LLM providers:

**Option 1: OpenAI**
```python
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
llm = ChatOpenAI(model="gpt-4", temperature=0.7)
```

**Option 2: Google Gemini (Free tier available)**
```python
api_key = "your-google-api-key"
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    temperature=0.3,
    google_api_key=api_key
)
```

## File Structure

```
.
├── langgraph_jury_deliberation.ipynb       # Main code
├── jurors/
│   ├── jurors.yaml                         # Detailed jury member profiles
│   ├── old_and_young.yaml                  # Age-diverse jury pool
│   ├── religious_and_secular.yaml          # Religion-diverse jury pool  
│   ├── republican_and_democratic.yaml      # Political-diverse jury pool
├── cases/
└── ├── Scenario 1.txt                      # Case scenarios (3 variations)
```

## Usage

### Quick Start

```python
# Run a complete deliberation with one line
run_deliberation(
    jury_file='jurors/republican_and_democratic.yaml',
    case_file="cases/Scenario 1.txt",
    scenario_number=1,
    total_rounds=3,
    save_to_file=True
)
```

### Step-by-Step Usage

1. **Load jury members**:
```python
initialize_with_yaml("jurors.yaml", total_rounds=3)
```

2. **Load a case**:
```python
initialize_with_case("Scenario 1.txt", scenario_number=1)
```

3. **Run deliberation**:
```python
main(interactive=False, save_to_file=True)
```


### Interactive Mode

Run the system in interactive mode for manual control:
```python
main(interactive=True)
```

Available commands:
- `load <yaml_file>` - Load jury members from YAML file
- `load <yaml_file> <rounds>` - Load jury and set deliberation rounds
- `rounds <number>` - Set number of deliberation rounds
- `case <case_file>` - Load case from text file
- `case <case_file> <scenario_number>` - Load specific scenario
- `scenarios <case_file>` - List available scenarios
- `deliberate` - Start deliberation with loaded case
- `deliberate nosave` - Run without saving to file
- `quit` - Exit


## Jury Member Format

Jury members can be defined in YAML with two structures:

### Detailed Structure (jurors.yaml)
```yaml
jury_member_1:
  first_name: Casey
  last_name: Brown
  age: 35 to 39 years
  gender: Male
  race: White alone
  education: Bachelor's degree
  occupation: Maintenance and repair workers
  income: $100,000 to $124,999
  religion: Catholic
  state: Pennsylvania
  biography: Casey Brown is a 37-year-old maintenance worker...
  role: Juror that is forced to participate
  goal: Have the case closed as soon as possible
```

### Simplified Structure
```yaml
jury_member_1:
  role: Juror in the case of {topic}
  goal: Listen impartially to the evidence...
  backstory: Carla is a retired high school civics teacher...
```

## Case Format

Cases are text files that can contain multiple scenarios:

```
Scenario 1: 
Background: Tomer and Stan are accused of murder...
Presenting the Decisive Evidence: The trial is underway...
```

## Output

Deliberations are saved as markdown files with:
- Timestamp and configuration details
- Full case description
- Round-by-round discussions
- Final verdicts from each juror
- Overall jury decision (Guilty/Not Guilty/Hung Jury)
- Color-coded speakers for easy reading

Each juror's response in the deliberation rounds includes their current stance declaration in the format `[Current stance: GUILTY/NOT GUILTY]`. 
This allows tracking of how individual juror opinions evolve throughout the multi-round deliberation process.

Example filename: `deliberation_republican_and_democratic_Scenario_1_scenario1_20250611_150544.md`

### Viewing Colored Output

The markdown files include HTML color styling for different speakers, which won't be visible in standard markdown viewers. To see the colored deliberation output:

1. Convert the markdown file to HTML using a web tool such as https://markdowntohtml.com/

2. Copy the contents of your deliberation .md file

3. Paste into the converter

4. View or save the resulting HTML to see speakers in their assigned colors


## Architecture

The system uses LangGraph to create a state machine with:
- **Moderator node**: Manages rounds and transitions
- **Jury member nodes**: Individual AI agents with personas
- **Final verdict node**: Collects votes and determines outcome
- **State management**: Tracks rounds, speakers, and discussion history

## Extending the System

### Adding New Jury Pools
Create a new YAML file following the structure examples above.

### Adding New Cases
Create text files with case details. Use "Scenario X:" headers for multiple scenarios.

### Customizing Deliberation Logic
Modify the `should_continue()` function to change flow control, or update jury member prompts in `create_jury_node()`.


## Troubleshooting

- **API Key Issues**: Ensure your API key is correctly set and has sufficient credits
- **Memory Issues**: For large juries or many rounds, consider using a more powerful model
- **File Not Found**: Check that all YAML and case files are in the correct directory
- **Slow Performance**: Gemini free tier has rate limits; consider upgrading or using OpenAI

## Citation

If you use this system in research, please cite:
```
[Your citation information here]
```

## License

[Your license information here]