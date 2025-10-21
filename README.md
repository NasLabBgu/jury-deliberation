# AI Agents Jury Deliberation Simulation

A sophisticated jury deliberation simulation system that uses Large Language Models (LLMs) to simulate realistic jury discussions and verdict decisions. The system is built using LangGraph and supports multiple LLM providers.

## Overview

This project simulates jury deliberations by creating AI-powered jury members with distinct backgrounds and personalities. Each juror analyzes case evidence, participates in multi-round discussions, and ultimately votes on a verdict.

## Features

- **Multi-round deliberations**: Configure the number of discussion rounds before final verdict
- **Diverse jury personas**: Load jury members from YAML files with detailed backgrounds
- **Multiple case scenarios**: Support for various cases (including scenarios based on "My Cousin Vinny")
- **LLM flexibility**: Works with OpenAI GPT-4 or Google Gemini models
- **Structured output**: Saves deliberations as formatted markdown files with speaker colors
- **Configurable jury size**: Simulate deliberations with 2-12 jury members
- **Intermediate verdict tracking**: Each juror declares their current stance (GUILTY/NOT GUILTY) at the end of each deliberation round
- **Command-line interface**: Easy-to-use CLI with interactive and batch modes
- **Modular architecture**: Well-structured Python package for extensibility

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ai-agents-jury-deliberation
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

### API Keys

The system supports two LLM providers and multiple ways to configure API keys:

#### **Method 1: Guided Setup (Recommended)**
```bash
python setup_api_key.py
```

#### **Method 2: .env File**
Create a `.env` file in the project root:
```bash
# Copy the example file
cp env.example .env

# Edit .env file with your API keys
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

#### **Method 3: Environment Variables**
```bash
# Google Gemini
export GOOGLE_API_KEY="your-google-api-key"

# OpenAI
export OPENAI_API_KEY="your-openai-api-key"
```

#### **Method 4: Legacy api_key File**
```bash
echo "your_google_api_key_here" > api_key
```

#### **API Key Priority Order:**
1. Environment variables (highest priority)
2. `.env` file
3. `api_key` file (legacy support)

Get your API keys from:
- Google Gemini: https://aistudio.google.com/app/apikey
- OpenAI: https://platform.openai.com/api-keys

## Project Structure

```
ai-agents-jury-deliberation/
├── main.py                           # Main CLI script
├── requirements.txt                  # Python dependencies
├── README.md                        # This file
├── jury_simulation/                 # Core simulation package
│   ├── __init__.py
│   ├── state.py                     # State definitions
│   ├── deliberation_simulator.py    # Main simulator orchestrator
│   └── langgraph_state_machine.py   # LangGraph workflow
├── agents/                          # AI agent implementations
│   ├── __init__.py
│   ├── juror.py                     # Individual juror agent
│   ├── moderator.py                 # Deliberation moderator
│   └── verdict_manager.py           # Verdict collection
├── config/                          # Configuration and data loading
│   ├── __init__.py
│   ├── data_loader.py               # YAML and case file loading
│   └── llm_manager.py               # LLM initialization
├── output/                          # Output formatting
│   ├── __init__.py
│   └── formatter.py                 # Markdown generation
├── jurors/                          # Jury member profiles
│   ├── jurors.yaml                  # Detailed jury member profiles
│   ├── old_and_young.yaml           # Age-diverse jury pool
│   ├── religious_and_secular.yaml   # Religion-diverse jury pool  
│   └── republican_and_democratic.yaml # Political-diverse jury pool
└── cases/                           # Case scenarios
    └── Scenario 1.txt               # Case scenarios (3 variations)
```

## Usage

### Command-Line Interface

The main entry point is the `main.py` script with comprehensive CLI options:

```bash
# Basic usage with jury and case files
python main.py --jury jurors/jurors.yaml --case cases/Scenario\ 1.txt --scenario 1

# Specify model and number of rounds
python main.py --jury jurors/republican_and_democratic.yaml \
               --case cases/Scenario\ 1.txt --scenario 2 \
               --model gemini-2.0-flash-001 --rounds 5

# Use OpenAI instead of Gemini
python main.py --jury jurors/jurors.yaml --case cases/Scenario\ 1.txt \
               --provider openai --model gpt-4

# Run without saving output
python main.py --jury jurors/jurors.yaml --case cases/Scenario\ 1.txt --no-save

# List available scenarios in a case file
python main.py --list-scenarios cases/Scenario\ 1.txt

# Show current configuration status
python main.py --status

# Run in interactive mode
python main.py --interactive
```

### Interactive Mode

Interactive mode provides a command-line interface for step-by-step configuration:

```bash
python main.py --interactive
```

Available commands in interactive mode:
- `load <yaml_file>` - Load jury members from YAML file
- `load <yaml_file> <rounds>` - Load jury members and set rounds
- `rounds <number>` - Set number of deliberation rounds
- `case <case_file>` - Load case from text file
- `case <case_file> <scenario_number>` - Load specific scenario
- `scenarios <case_file>` - List available scenarios
- `deliberate` - Start deliberation with loaded case
- `deliberate nosave` - Run without saving to file
- `status` - Show current configuration
- `quit` - Exit

### Programmatic Usage

You can also use the system programmatically:

```python
from jury_simulation.deliberation_simulator import DeliberationSimulator
from config.llm_manager import llm_manager

# Initialize LLM
llm_manager.initialize_gemini("gemini-2.0-flash-001")

# Create simulator
simulator = DeliberationSimulator()

# Load jury and case
simulator.load_jury_from_yaml("jurors/jurors.yaml", total_rounds=3)
simulator.load_case_from_file("cases/Scenario 1.txt", scenario_number=1)

# Run deliberation
output_file = simulator.run_deliberation(save_to_file=True)
print(f"Deliberation saved to: {output_file}")
```

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

Scenario 2: 
Background: Tomer and Stan are accused of murder...
Presenting the Decisive Evidence: The trial is underway...
```

## Output

Deliberations are saved as markdown files in the `output/deliberations/` directory with:
- Timestamp and configuration details
- Full case description
- Round-by-round discussions
- Final verdicts from each juror
- Overall jury decision (Guilty/Not Guilty/Hung Jury)
- Color-coded speakers for easy reading

Each juror's response includes their current stance declaration in the format `[Current stance: GUILTY/NOT GUILTY]`, allowing tracking of how individual juror opinions evolve throughout the multi-round deliberation process.

**Output Location:** `output/deliberations/`
**Example filename:** `deliberation_jurors_Scenario_1_scenario1_20250611_150544.md`

### Viewing Colored Output

The markdown files include HTML color styling for different speakers. To see the colored deliberation output:

1. Convert the markdown file to HTML using a web tool such as https://markdowntohtml.com/
2. Copy the contents of your deliberation .md file
3. Paste into the converter
4. View or save the resulting HTML to see speakers in their assigned colors

## Architecture

The system uses a modular architecture with clear separation of concerns:

- **LangGraph State Machine**: Manages the deliberation workflow
- **Agent Classes**: Individual AI agents (Juror, Moderator, VerdictManager)
- **Data Loaders**: Handle YAML and case file loading
- **Output Formatters**: Generate structured markdown output
- **LLM Manager**: Handles LLM initialization and configuration

### Core Components

- **DeliberationSimulator**: Main orchestrator that coordinates the entire process
- **LangGraphStateMachine**: LangGraph-based workflow engine
- **Juror**: Individual jury member with personality and background
- **Moderator**: Manages deliberation rounds and flow control
- **VerdictManager**: Collects and processes final verdicts

## Extending the System

### Adding New Jury Pools
Create a new YAML file following the structure examples above and place it in the `jurors/` directory.

### Adding New Cases
Create text files with case details and place them in the `cases/` directory. Use "Scenario X:" headers for multiple scenarios.

### Customizing Deliberation Logic
Modify the agent classes in the `agents/` package to customize deliberation behavior, or update the state machine in `jury_simulation/langgraph_state_machine.py`.

### Adding New LLM Providers
Extend the `LLMManager` class in `config/llm_manager.py` to support additional LLM providers.

## Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API key is correctly set and has sufficient credits
- **Memory Issues**: For large juries or many rounds, consider using a more powerful model
- **File Not Found**: Check that all YAML and case files are in the correct directory
- **Slow Performance**: Gemini free tier has rate limits; consider upgrading or using OpenAI
- **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`

### Rate Limiting

The system includes automatic rate limiting and retry logic for Google Gemini API:
- **15 requests per minute** for gemini-2.0-flash
- **1,500 requests per day** for free tier

The system will automatically retry with exponential backoff when rate limits are hit.

### Getting Help

Run `python main.py --help` for detailed CLI options, or use `python main.py --status` to check your current configuration.

## Citation

If you use this system in research, please cite:
```
[Your citation information here]
```

## License

[Your license information here]