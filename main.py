#!/usr/bin/env python3
"""
Main script for AI-powered jury deliberation simulation.

This script provides a command-line interface for running jury deliberation
simulations with configurable jury members, cases, and deliberation parameters.
"""

import argparse
import sys
import os
from typing import Optional

from jury_simulation.deliberation_simulator import DeliberationSimulator
from config.llm_manager import llm_manager
from config.data_loader import list_scenarios_in_file
from output.formatter import output_formatter


def main():
    """Main entry point for the jury deliberation simulation."""
    parser = argparse.ArgumentParser(
        description="AI-powered jury deliberation simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default jury and case
  python main.py --jury jurors/jurors.yaml --case cases/Scenario\ 1.txt --scenario 1
  
  # Run with specific model and rounds
  python main.py --jury jurors/republican_and_democratic.yaml --case cases/Scenario\ 1.txt --scenario 2 --model gemini-2.0-flash-001 --rounds 5
  
  # Run interactive mode
  python main.py --interactive
  
  # List scenarios in a case file
  python main.py --list-scenarios cases/Scenario\ 1.txt
        """
    )
    
    # Jury configuration
    parser.add_argument(
        "--jury", "-j",
        type=str,
        help="Path to YAML file containing jury member profiles"
    )
    
    # Case configuration
    parser.add_argument(
        "--case", "-c",
        type=str,
        help="Path to case file"
    )
    parser.add_argument(
        "--scenario", "-s",
        type=int,
        help="Scenario number (if case file contains multiple scenarios)"
    )
    
    # Deliberation parameters
    parser.add_argument(
        "--rounds", "-r",
        type=int,
        default=3,
        help="Number of deliberation rounds (default: 3)"
    )
    
    # LLM configuration
    parser.add_argument(
        "--model", "-m",
        type=str,
        default="gemini-2.0-flash-001",
        help="LLM model to use (default: gemini-2.0-flash-001)"
    )
    parser.add_argument(
        "--provider",
        choices=["gemini", "openai"],
        default="gemini",
        help="LLM provider to use (default: gemini)"
    )
    
    # Output options
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save deliberation to markdown file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Directory to save output files (default: output/deliberations/)"
    )
    
    # Utility options
    parser.add_argument(
        "--list-scenarios",
        type=str,
        metavar="CASE_FILE",
        help="List available scenarios in a case file"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show current configuration status"
    )
    
    args = parser.parse_args()
    
    # Handle utility commands
    if args.list_scenarios:
        list_scenarios_command(args.list_scenarios)
        return
    
    if args.status:
        show_status()
        return
    
    # Initialize LLM
    if not initialize_llm(args.provider, args.model):
        print("❌ Failed to initialize LLM. Exiting.")
        return 1
    
    # Create simulator
    simulator = DeliberationSimulator()
    
    # Handle interactive mode
    if args.interactive:
        return run_interactive_mode(simulator)
    
    # Validate required arguments for non-interactive mode
    if not args.jury:
        print("❌ Error: --jury is required for non-interactive mode")
        print("Use --interactive for interactive mode or specify --jury")
        return 1
    
    if not args.case:
        print("❌ Error: --case is required for non-interactive mode")
        print("Use --interactive for interactive mode or specify --case")
        return 1
    
    # Load jury members
    try:
        simulator.load_jury_from_yaml(args.jury, args.rounds)
    except Exception as e:
        print(f"❌ Error loading jury file: {e}")
        return 1
    
    # Load case
    try:
        simulator.load_case_from_file(args.case, args.scenario)
    except Exception as e:
        print(f"❌ Error loading case file: {e}")
        return 1
    
    # Run deliberation
    print("🚀 Starting deliberation...")
    try:
        output_file = simulator.run_deliberation(save_to_file=not args.no_save)
        if output_file and not args.no_save:
            from output.formatter import output_formatter
            relative_path = output_formatter.get_relative_output_path()
            print(f"📄 Deliberation saved to: {relative_path}/")
            print(f"📁 Full path: {output_file}")
    except Exception as e:
        print(f"❌ Error during deliberation: {e}")
        return 1
    
    print("🏁 Deliberation completed!")
    return 0


def initialize_llm(provider: str, model: str) -> bool:
    """Initialize the LLM with the specified provider and model.
    
    Args:
        provider: LLM provider ("gemini" or "openai")
        model: Model name
        
    Returns:
        True if initialization successful, False otherwise
    """
    print(f"🤖 Initializing {provider} LLM with model: {model}")
    
    if provider == "gemini":
        llm = llm_manager.initialize_gemini(model)
    elif provider == "openai":
        llm = llm_manager.initialize_openai(model)
    else:
        print(f"❌ Unknown provider: {provider}")
        return False
    
    if llm is None:
        return False
    
    # Test connection
    return llm_manager.test_connection()


def list_scenarios_command(case_file: str):
    """List available scenarios in a case file.
    
    Args:
        case_file: Path to the case file
    """
    print(f"📋 Listing scenarios in: {case_file}")
    scenarios = list_scenarios_in_file(case_file)
    
    if scenarios:
        print(f"Available scenarios in {case_file}:")
        for num, title in scenarios:
            print(f"  {num}: {title}")
    else:
        print("No scenarios found or file error")


def show_status():
    """Show current configuration status."""
    print("📊 Current Configuration Status:")
    print(f"LLM Initialized: {llm_manager.is_initialized()}")
    
    if llm_manager.is_initialized():
        model_info = llm_manager.get_model_info()
        print(f"Model: {model_info['model']}")
        print(f"API Key Source: {model_info['api_key_source']}")
    
    relative_path = output_formatter.get_relative_output_path()
    print(f"Output Directory: {relative_path}/")
    print(f"Full Path: {output_formatter.get_download_directory()}")
    
    # List available output files
    files = output_formatter.list_download_files()
    if files:
        print(f"Available output files ({len(files)}):")
        for filename, _ in files[:5]:  # Show first 5
            print(f"  - {filename}")
        if len(files) > 5:
            print(f"  ... and {len(files) - 5} more")
    else:
        print("No output files available")


def run_interactive_mode(simulator: DeliberationSimulator) -> int:
    """Run the simulator in interactive mode.
    
    Args:
        simulator: The deliberation simulator instance
        
    Returns:
        Exit code
    """
    print("=== INTERACTIVE JURY DELIBERATION MODE ===")
    print("Commands:")
    print("• 'load <yaml_file>' - Load jury members from YAML file")
    print("• 'load <yaml_file> <rounds>' - Load jury members and set rounds")
    print("• 'rounds <number>' - Set number of deliberation rounds")
    print("• 'case <case_file>' - Load case from text file")
    print("• 'case <case_file> <scenario_number>' - Load specific scenario from file")
    print("• 'scenarios <case_file>' - List available scenarios in file")
    print("• 'deliberate' - Start deliberation with loaded case")
    print("• 'deliberate nosave' - Start deliberation without saving to file")
    print("• 'status' - Show current configuration")
    print("• 'quit', 'exit', or 'q' - Stop")
    print("• Or type case details directly for immediate deliberation\n")

    while True:
        try:
            user_input = input("Enter command or case details: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            # Check if user wants to load YAML file
            if user_input.lower().startswith("load "):
                parts = user_input[5:].strip().split()
                yaml_file = parts[0]
                rounds = int(parts[1]) if len(parts) > 1 else 3

                try:
                    simulator.load_jury_from_yaml(yaml_file, rounds)
                    print("Jury members loaded successfully!")
                except Exception as e:
                    print(f"Error loading YAML file: {e}")
                continue

            # Check if user wants to set rounds
            if user_input.lower().startswith("rounds "):
                try:
                    rounds = int(user_input[7:].strip())
                    simulator.set_deliberation_rounds(rounds)
                except ValueError:
                    print("Invalid number of rounds. Please enter a number.")
                continue

            # Check if user wants to load case file
            if user_input.lower().startswith("case "):
                parts = user_input[5:].strip().split()
                case_file = parts[0]
                scenario_num = int(parts[1]) if len(parts) > 1 else None

                try:
                    simulator.load_case_from_file(case_file, scenario_num)
                    print("Case loaded successfully!")
                except Exception as e:
                    print(f"Error loading case file: {e}")
                continue

            # Check if user wants to list scenarios
            if user_input.lower().startswith("scenarios "):
                case_file = user_input[10:].strip()
                scenarios = list_scenarios_in_file(case_file)
                if scenarios:
                    print(f"Available scenarios in {case_file}:")
                    for num, title in scenarios:
                        print(f"  {num}: {title}")
                else:
                    print("No scenarios found or file error")
                continue

            # Check if user wants to deliberate with loaded case
            if user_input.lower().startswith("deliberate"):
                if simulator.current_case is None:
                    print("No case loaded. Use 'case <filename>' to load a case first.")
                    continue

                # Check if user wants to save or not
                save_file = "nosave" not in user_input.lower()

                print(f"\n🏛️ Starting deliberation with loaded case...\n")
                simulator.run_deliberation(save_to_file=save_file)
                print("\n" + "="*50 + "\n")
                continue

            # Check if user wants status
            if user_input.lower() == "status":
                status = simulator.get_status()
                print("\n📊 Current Status:")
                for key, value in status.items():
                    print(f"  {key}: {value}")
                print()
                continue

            # Treat as direct case input for immediate deliberation
            if user_input.strip():
                print(f"\nCase: {user_input}\n")
                simulator.set_case_directly(user_input)
                simulator.run_deliberation()
                print("\n" + "="*50 + "\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            print("Trying with fallback example...")
            # Fallback example
            user_input = "John stole a laptop worth $1200 from a coffee shop. He was caught with it 3 days later but claims he bought it from someone on the street for $300. He has no prior record but recently lost his job."
            print("Case: " + user_input)
            simulator.set_case_directly(user_input)
            simulator.run_deliberation()
            break

    return 0


if __name__ == "__main__":
    sys.exit(main())
