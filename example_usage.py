#!/usr/bin/env python3
"""
Example usage of the refactored AI Agents Jury Deliberation system.

This script demonstrates how to use the new modular structure programmatically.
"""

import os
from jury_simulation.deliberation_simulator import DeliberationSimulator
from config.llm_manager import llm_manager


def example_programmatic_usage():
    """Example of using the system programmatically."""
    print("=== EXAMPLE: PROGRAMMATIC USAGE ===")
    
    # Step 1: Initialize LLM (you'll need to set your API key)
    print("1. Initializing LLM...")
    
    # Check if API key is available
    if not os.environ.get('GOOGLE_API_KEY'):
        print("⚠️  No GOOGLE_API_KEY found in environment variables.")
        print("   Please set your API key: export GOOGLE_API_KEY='your-key-here'")
        print("   Or create an 'api_key' file with your key")
        return False
    
    # Initialize Gemini LLM
    llm = llm_manager.initialize_gemini("gemini-2.0-flash-001")
    if not llm:
        print("❌ Failed to initialize LLM")
        return False
    
    # Test connection
    if not llm_manager.test_connection():
        print("❌ LLM connection test failed")
        return False
    
    # Step 2: Create simulator
    print("2. Creating deliberation simulator...")
    simulator = DeliberationSimulator()
    
    # Step 3: Load jury members
    print("3. Loading jury members...")
    try:
        simulator.load_jury_from_yaml("jurors/jurors.yaml", total_rounds=2)  # Reduced rounds for demo
        print(f"   Loaded {len(simulator.jury_backgrounds)} jury members")
    except Exception as e:
        print(f"❌ Error loading jury: {e}")
        return False
    
    # Step 4: Load case
    print("4. Loading case...")
    try:
        simulator.load_case_from_file("cases/Scenario 1.txt", scenario_number=1)
        print("   Case loaded successfully")
    except Exception as e:
        print(f"❌ Error loading case: {e}")
        return False
    
    # Step 5: Show status
    print("5. Current status:")
    status = simulator.get_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    # Step 6: Run deliberation
    print("6. Running deliberation...")
    try:
        output_file = simulator.run_deliberation(save_to_file=True)
        if output_file:
            from output.formatter import output_formatter
            relative_path = output_formatter.get_relative_output_path()
            print(f"✅ Deliberation completed and saved to: {relative_path}/")
            print(f"📁 Full path: {output_file}")
        else:
            print("✅ Deliberation completed (not saved)")
    except Exception as e:
        print(f"❌ Error during deliberation: {e}")
        return False
    
    print("\n🎉 Example completed successfully!")
    return True


def example_simple_case():
    """Example with a simple case input."""
    print("\n=== EXAMPLE: SIMPLE CASE INPUT ===")
    
    # Check LLM
    if not llm_manager.is_initialized():
        print("⚠️  LLM not initialized. Please run the programmatic example first.")
        return False
    
    # Create simulator
    simulator = DeliberationSimulator()
    
    # Load jury
    try:
        simulator.load_jury_from_yaml("jurors/republican_and_democratic.yaml", total_rounds=1)  # Single round for demo
    except Exception as e:
        print(f"❌ Error loading jury: {e}")
        return False
    
    # Set simple case directly
    simple_case = """
    John is accused of stealing a $50 item from a convenience store. 
    The store owner testifies that he saw John take the item and leave without paying. 
    John claims he forgot to pay and offers to pay now. 
    There is no video evidence and no other witnesses.
    """
    
    simulator.set_case_directly(simple_case)
    print("Simple case set successfully")
    
    # Run deliberation
    try:
        output_file = simulator.run_deliberation(save_to_file=True)
        if output_file:
            from output.formatter import output_formatter
            relative_path = output_formatter.get_relative_output_path()
            print(f"✅ Simple deliberation completed and saved to: {relative_path}/")
            print(f"📁 Full path: {output_file}")
        else:
            print("✅ Simple deliberation completed (not saved)")
    except Exception as e:
        print(f"❌ Error during simple deliberation: {e}")
        return False
    
    return True


def main():
    """Main function to run examples."""
    print("AI AGENTS JURY DELIBERATION - EXAMPLE USAGE")
    print("=" * 50)
    
    # Run programmatic example
    success1 = example_programmatic_usage()
    
    if success1:
        # Run simple case example
        success2 = example_simple_case()
        
        if success2:
            print("\n🎉 ALL EXAMPLES COMPLETED SUCCESSFULLY!")
            print("\nThe refactored system is working correctly.")
            print("You can now use the CLI interface:")
            print("  python main.py --help")
            print("  python main.py --interactive")
        else:
            print("\n⚠️  Simple case example failed, but programmatic example succeeded.")
    else:
        print("\n❌ Programmatic example failed. Please check your API key and dependencies.")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
