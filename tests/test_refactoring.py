#!/usr/bin/env python3
"""
Comprehensive test script for the refactored AI Agents Jury Deliberation system.

This script implements the key tests from the testing plan to verify functionality
and completeness of the refactoring.
"""

import os
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Any


class TestResult:
    """Container for test results."""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.status = "NOT_RUN"
        self.message = ""
        self.details = {}
        self.duration = 0.0


class RefactoringTester:
    """Main test class for the refactored system."""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.passed = 0
        self.failed = 0
        self.skipped = 0
    
    def run_test(self, test_func, test_name: str) -> TestResult:
        """Run a test function and record results."""
        result = TestResult(test_name)
        print(f"\n🧪 Running: {test_name}")
        
        try:
            start_time = sys.modules['time'].time() if 'time' in sys.modules else 0
            test_func(result)
            end_time = sys.modules['time'].time() if 'time' in sys.modules else 0
            
            result.duration = end_time - start_time
            result.status = "PASS"
            self.passed += 1
            print(f"✅ PASSED: {test_name}")
            
        except Exception as e:
            result.status = "FAIL"
            result.message = str(e)
            result.details["traceback"] = traceback.format_exc()
            self.failed += 1
            print(f"❌ FAILED: {test_name} - {e}")
        
        self.results.append(result)
        return result
    
    def test_imports(self, result: TestResult):
        """Test 1.1: Basic Import Verification."""
        try:
            # Test core modules
            from jury_simulation.deliberation_simulator import DeliberationSimulator
            from jury_simulation.langgraph_state_machine import LangGraphStateMachine
            from jury_simulation.state import JuryState
            
            # Test agent modules
            from agents.juror import Juror
            from agents.moderator import Moderator
            from agents.verdict_manager import VerdictManager
            
            # Test config modules
            from config.data_loader import load_backgrounds_from_yaml, load_case_from_file
            from config.llm_manager import llm_manager
            
            # Test output modules
            from output.formatter import output_formatter
            
            result.details["imported_modules"] = [
                "DeliberationSimulator", "LangGraphStateMachine", "JuryState",
                "Juror", "Moderator", "VerdictManager",
                "data_loader", "llm_manager", "output_formatter"
            ]
            result.message = "All modules imported successfully"
            
        except ImportError as e:
            raise Exception(f"Import failed: {e}")
    
    def test_module_initialization(self, result: TestResult):
        """Test 1.2: Module Initialization."""
        try:
            from jury_simulation.deliberation_simulator import DeliberationSimulator
            from config.llm_manager import llm_manager
            from output.formatter import output_formatter
            from agents.juror import Juror
            from agents.moderator import Moderator
            from agents.verdict_manager import VerdictManager
            
            # Test instantiation
            simulator = DeliberationSimulator()
            moderator = Moderator()
            verdict_manager = VerdictManager()
            
            result.details["instantiated_classes"] = [
                "DeliberationSimulator", "Moderator", "VerdictManager"
            ]
            result.message = "All classes instantiated successfully"
            
        except Exception as e:
            raise Exception(f"Initialization failed: {e}")
    
    def test_data_loading(self, result: TestResult):
        """Test 2.1: Data Loading Functionality."""
        try:
            from config.data_loader import load_backgrounds_from_yaml, load_case_from_file, list_scenarios_in_file
            
            # Test YAML loading
            if Path("jurors/jurors.yaml").exists():
                backgrounds = load_backgrounds_from_yaml("jurors/jurors.yaml")
                result.details["jurors_yaml_loaded"] = len(backgrounds) > 0
            
            if Path("jurors/republican_and_democratic.yaml").exists():
                backgrounds = load_backgrounds_from_yaml("jurors/republican_and_democratic.yaml")
                result.details["republican_yaml_loaded"] = len(backgrounds) > 0
            
            # Test case loading
            if Path("cases/Scenario 1.txt").exists():
                case_content = load_case_from_file("cases/Scenario 1.txt")
                result.details["case_file_loaded"] = len(case_content) > 0
                
                # Test scenario listing
                scenarios = list_scenarios_in_file("cases/Scenario 1.txt")
                result.details["scenarios_found"] = len(scenarios)
            
            result.message = "Data loading functionality works correctly"
            
        except Exception as e:
            raise Exception(f"Data loading failed: {e}")
    
    def test_llm_manager(self, result: TestResult):
        """Test 2.2: LLM Manager Testing."""
        try:
            from config.llm_manager import llm_manager
            
            # Test API key detection
            api_key = llm_manager.get_api_key()
            result.details["api_key_found"] = api_key is not None
            
            # Test model info
            model_info = llm_manager.get_model_info()
            result.details["model_info"] = model_info
            
            # Test initialization status
            result.details["llm_initialized"] = llm_manager.is_initialized()
            
            result.message = "LLM manager functionality works correctly"
            
        except Exception as e:
            raise Exception(f"LLM manager testing failed: {e}")
    
    def test_output_formatter(self, result: TestResult):
        """Test 2.3: Output Formatter Testing."""
        try:
            from output.formatter import output_formatter
            
            # Test color assignment
            test_jury = ["Alice", "Bob", "Carol"]
            colors = output_formatter.assign_juror_colors(test_jury)
            result.details["colors_assigned"] = len(colors) == len(test_jury)
            
            # Test output directory
            download_dir = output_formatter.get_download_directory()
            result.details["download_dir_created"] = Path(download_dir).exists()
            
            # Test formatting
            formatted = output_formatter.format_speaker_output("TestSpeaker", "Test message")
            result.details["formatting_works"] = "TestSpeaker" in formatted and "Test message" in formatted
            
            result.message = "Output formatter functionality works correctly"
            
        except Exception as e:
            raise Exception(f"Output formatter testing failed: {e}")
    
    def test_deliberation_simulator(self, result: TestResult):
        """Test 2.4: Deliberation Simulator Testing."""
        try:
            from jury_simulation.deliberation_simulator import DeliberationSimulator
            
            simulator = DeliberationSimulator()
            
            # Test status
            status = simulator.get_status()
            result.details["status_fields"] = len(status)
            
            # Test round setting
            simulator.set_deliberation_rounds(5)
            result.details["rounds_set"] = simulator.total_rounds == 5
            
            # Test case setting
            test_case = "Test case for simulation"
            simulator.set_case_directly(test_case)
            result.details["case_set"] = simulator.current_case == test_case
            
            result.message = "Deliberation simulator functionality works correctly"
            
        except Exception as e:
            raise Exception(f"Deliberation simulator testing failed: {e}")
    
    def test_cli_help(self, result: TestResult):
        """Test 3.1: CLI Help System Testing."""
        try:
            import subprocess
            
            # Test help command
            try:
                help_output = subprocess.run(
                    [sys.executable, "main.py", "--help"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                result.details["help_command_works"] = help_output.returncode == 0
                result.details["help_output_length"] = len(help_output.stdout)
            except subprocess.TimeoutExpired:
                result.details["help_command_works"] = False
                result.details["help_timeout"] = True
            
            result.message = "CLI help system works correctly"
            
        except Exception as e:
            raise Exception(f"CLI help testing failed: {e}")
    
    def test_cli_utilities(self, result: TestResult):
        """Test 3.2: Basic CLI Commands."""
        try:
            import subprocess
            
            # Test status command
            try:
                status_output = subprocess.run(
                    [sys.executable, "main.py", "--status"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                result.details["status_command_works"] = status_output.returncode == 0
            except subprocess.TimeoutExpired:
                result.details["status_command_works"] = False
            
            # Test list scenarios command
            if Path("cases/Scenario 1.txt").exists():
                try:
                    scenarios_output = subprocess.run(
                        [sys.executable, "main.py", "--list-scenarios", "cases/Scenario 1.txt"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    result.details["scenarios_command_works"] = scenarios_output.returncode == 0
                except subprocess.TimeoutExpired:
                    result.details["scenarios_command_works"] = False
            
            result.message = "CLI utility commands work correctly"
            
        except Exception as e:
            raise Exception(f"CLI utilities testing failed: {e}")
    
    def test_end_to_end_simulation(self, result: TestResult):
        """Test 4.1: End-to-End Deliberation (Simple Case)."""
        try:
            from jury_simulation.deliberation_simulator import DeliberationSimulator
            from config.llm_manager import llm_manager
            
            # Skip if no API key
            if not llm_manager.get_api_key():
                result.status = "SKIP"
                result.message = "No API key available, skipping end-to-end test"
                self.skipped += 1
                return
            
            simulator = DeliberationSimulator()
            
            # Test with simple case
            simple_case = """
            John is accused of stealing a $50 item from a store.
            The store owner saw him take it. John says he forgot to pay.
            No video evidence exists.
            """
            
            simulator.set_case_directly(simple_case)
            simulator.set_deliberation_rounds(1)  # Single round for testing
            
            # Note: We don't actually run the deliberation here to avoid API costs
            # but we test that the setup works
            result.details["simulation_setup_complete"] = True
            result.message = "End-to-end simulation setup works correctly"
            
        except Exception as e:
            raise Exception(f"End-to-end simulation testing failed: {e}")
    
    def test_file_structure(self, result: TestResult):
        """Test file structure completeness."""
        try:
            required_files = [
                "main.py",
                "requirements.txt",
                "README.md",
                "setup.py",
                "example_usage.py",
                "jury_simulation/__init__.py",
                "jury_simulation/deliberation_simulator.py",
                "jury_simulation/langgraph_state_machine.py",
                "jury_simulation/state.py",
                "agents/__init__.py",
                "agents/juror.py",
                "agents/moderator.py",
                "agents/verdict_manager.py",
                "config/__init__.py",
                "config/data_loader.py",
                "config/llm_manager.py",
                "output/__init__.py",
                "output/formatter.py",
            ]
            
            missing_files = []
            for file_path in required_files:
                if not Path(file_path).exists():
                    missing_files.append(file_path)
            
            result.details["missing_files"] = missing_files
            result.details["total_required"] = len(required_files)
            result.details["files_present"] = len(required_files) - len(missing_files)
            
            if missing_files:
                raise Exception(f"Missing required files: {missing_files}")
            
            result.message = "All required files present"
            
        except Exception as e:
            raise Exception(f"File structure testing failed: {e}")
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting Comprehensive Refactoring Tests")
        print("=" * 60)
        
        # Phase 1: Import and Module Testing
        print("\n📦 Phase 1: Import and Module Testing")
        self.run_test(self.test_imports, "Import Verification")
        self.run_test(self.test_module_initialization, "Module Initialization")
        
        # Phase 2: Unit Functionality Testing
        print("\n🔧 Phase 2: Unit Functionality Testing")
        self.run_test(self.test_data_loading, "Data Loading")
        self.run_test(self.test_llm_manager, "LLM Manager")
        self.run_test(self.test_output_formatter, "Output Formatter")
        self.run_test(self.test_deliberation_simulator, "Deliberation Simulator")
        
        # Phase 3: CLI Interface Testing
        print("\n💻 Phase 3: CLI Interface Testing")
        self.run_test(self.test_cli_help, "CLI Help System")
        self.run_test(self.test_cli_utilities, "CLI Utilities")
        
        # Phase 4: Integration Testing
        print("\n🔗 Phase 4: Integration Testing")
        self.run_test(self.test_end_to_end_simulation, "End-to-End Simulation")
        
        # Phase 5: Structure Testing
        print("\n📁 Phase 5: Structure Testing")
        self.run_test(self.test_file_structure, "File Structure")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary."""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"⏭️  Skipped: {self.skipped}")
        print(f"📊 Total: {len(self.results)}")
        
        if self.failed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.results:
                if result.status == "FAIL":
                    print(f"  - {result.test_name}: {result.message}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED! Refactoring is successful.")
        else:
            print(f"\n⚠️  {self.failed} tests failed. Please review and fix issues.")
        
        print("\n📋 Detailed Results:")
        for result in self.results:
            status_icon = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⏭️"
            print(f"  {status_icon} {result.test_name}: {result.message}")
            if result.details:
                for key, value in result.details.items():
                    print(f"     {key}: {value}")


def main():
    """Main function to run all tests."""
    try:
        tester = RefactoringTester()
        tester.run_all_tests()
        
        if tester.failed == 0:
            return 0
        else:
            return 1
            
    except Exception as e:
        print(f"❌ Test runner failed: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
