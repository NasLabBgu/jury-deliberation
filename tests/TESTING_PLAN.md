# Testing Plan: AI Agents Jury Deliberation Refactoring

## Overview

This document outlines a comprehensive testing plan to verify the functionality and completeness of the refactored AI Agents Jury Deliberation project. The plan covers import testing, functionality verification, CLI interface testing, and end-to-end integration testing.

## Testing Environment Setup

### Prerequisites
- Python 3.8+ installed
- API key configured (Google Gemini or OpenAI)
- All dependencies installed

### Test Categories
1. **Import and Module Testing**
2. **Unit Functionality Testing**
3. **CLI Interface Testing**
4. **Integration Testing**
5. **Error Handling Testing**
6. **Performance and Edge Case Testing**

---

## Phase 1: Import and Module Testing

### Test 1.1: Basic Import Verification
**Objective:** Verify all modules can be imported without errors

**Steps:**
1. Create a test script to import all modules
2. Test each module individually
3. Verify no circular import issues

**Test Script:**
```python
# test_imports.py
def test_all_imports():
    try:
        # Core modules
        from jury_simulation.deliberation_simulator import DeliberationSimulator
        from jury_simulation.langgraph_state_machine import LangGraphStateMachine
        from jury_simulation.state import JuryState
        
        # Agent modules
        from agents.juror import Juror
        from agents.moderator import Moderator
        from agents.verdict_manager import VerdictManager
        
        # Config modules
        from config.data_loader import load_backgrounds_from_yaml, load_case_from_file
        from config.llm_manager import llm_manager
        
        # Output modules
        from output.formatter import output_formatter
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
```

**Expected Result:** All imports successful, no errors

### Test 1.2: Module Initialization
**Objective:** Verify all classes can be instantiated

**Steps:**
1. Test DeliberationSimulator instantiation
2. Test LLMManager initialization
3. Test OutputFormatter creation
4. Test individual agent creation

**Expected Result:** All classes instantiate without errors

---

## Phase 2: Unit Functionality Testing

### Test 2.1: Data Loading Functionality
**Objective:** Verify YAML and case file loading works correctly

**Steps:**
1. Test YAML jury profile loading
2. Test case file loading with single scenario
3. Test case file loading with multiple scenarios
4. Test error handling for missing files

**Test Cases:**
- `jurors/jurors.yaml` (detailed structure)
- `jurors/republican_and_democratic.yaml` (simplified structure)
- `cases/Scenario 1.txt` (multiple scenarios)
- Non-existent files (error handling)

**Expected Result:** All files load correctly, proper error messages for missing files

### Test 2.2: LLM Manager Testing
**Objective:** Verify LLM initialization and management

**Steps:**
1. Test API key detection (environment variable vs file)
2. Test Gemini LLM initialization
3. Test OpenAI LLM initialization (if available)
4. Test connection testing functionality
5. Test error handling for invalid API keys

**Expected Result:** LLM initializes correctly, connection test passes, proper error handling

### Test 2.3: Output Formatter Testing
**Objective:** Verify output formatting and file generation

**Steps:**
1. Test color assignment for jury members
2. Test markdown formatting
3. Test file saving functionality
4. Test filename generation
5. Test output buffer management

**Expected Result:** Proper formatting, files saved correctly, colors assigned

---

## Phase 3: CLI Interface Testing

### Test 3.1: Help System Testing
**Objective:** Verify CLI help system works correctly

**Steps:**
1. Test main help: `python main.py --help`
2. Test argument parsing
3. Verify all options are documented
4. Test example commands in help text

**Expected Result:** Comprehensive help displayed, all options documented

### Test 3.2: Basic CLI Commands
**Objective:** Test core CLI functionality

**Steps:**
1. Test status command: `python main.py --status`
2. Test list scenarios: `python main.py --list-scenarios cases/Scenario\ 1.txt`
3. Test invalid arguments (error handling)
4. Test missing required arguments

**Expected Result:** Commands execute correctly, proper error messages

### Test 3.3: Interactive Mode Testing
**Objective:** Verify interactive mode functionality

**Steps:**
1. Start interactive mode: `python main.py --interactive`
2. Test help command in interactive mode
3. Test status command in interactive mode
4. Test quit functionality
5. Test invalid commands

**Expected Result:** Interactive mode starts, commands work, proper exit

---

## Phase 4: Integration Testing

### Test 4.1: End-to-End Deliberation (Simple Case)
**Objective:** Test complete deliberation with simple case

**Steps:**
1. Set up API key
2. Initialize LLM
3. Load default jury from YAML
4. Create simple test case
5. Run deliberation with minimal rounds
6. Verify output generation

**Test Case:**
```python
# Simple test case
test_case = """
John is accused of stealing a $50 item from a store.
The store owner saw him take it. John says he forgot to pay.
No video evidence exists.
"""
```

**Expected Result:** Complete deliberation runs, output generated, no errors

### Test 4.2: End-to-End Deliberation (Complex Case)
**Objective:** Test with real case scenarios

**Steps:**
1. Load `jurors/jurors.yaml`
2. Load `cases/Scenario 1.txt` scenario 1
3. Run 3-round deliberation
4. Verify verdict collection
5. Check output file generation

**Expected Result:** Multi-round deliberation completes, verdicts collected, markdown file saved

### Test 4.3: Different Jury Configurations
**Objective:** Test various jury configurations

**Steps:**
1. Test with `jurors/jurors.yaml` (detailed structure)
2. Test with `jurors/republican_and_democratic.yaml` (simplified structure)
3. Test with `jurors/old_and_young.yaml`
4. Test with `jurors/religious_and_secular.yaml`

**Expected Result:** All jury configurations work correctly

### Test 4.4: Different Case Scenarios
**Objective:** Test all case scenarios

**Steps:**
1. Test Scenario 1 from `cases/Scenario 1.txt`
2. Test Scenario 2 from `cases/Scenario 1.txt`
3. Test Scenario 3 from `cases/Scenario 1.txt`
4. Test direct case input

**Expected Result:** All scenarios process correctly

---

## Phase 5: Error Handling Testing

### Test 5.1: Missing Files Testing
**Objective:** Verify graceful handling of missing files

**Steps:**
1. Test with non-existent jury file
2. Test with non-existent case file
3. Test with invalid scenario number
4. Test with malformed YAML files

**Expected Result:** Clear error messages, graceful failure

### Test 5.2: API Key Testing
**Objective:** Test various API key scenarios

**Steps:**
1. Test with no API key
2. Test with invalid API key
3. Test with expired API key
4. Test rate limiting scenarios

**Expected Result:** Proper error messages, graceful handling

### Test 5.3: Network and API Testing
**Objective:** Test network-related issues

**Steps:**
1. Test with no internet connection
2. Test with API quota exceeded
3. Test with API rate limiting
4. Test with timeout scenarios

**Expected Result:** Proper retry logic, clear error messages

---

## Phase 6: Performance and Edge Case Testing

### Test 6.1: Large Jury Testing
**Objective:** Test with maximum jury size

**Steps:**
1. Create test YAML with 12 jury members
2. Run deliberation
3. Monitor memory usage
4. Check performance

**Expected Result:** Handles large juries without issues

### Test 6.2: Many Rounds Testing
**Objective:** Test with maximum rounds

**Steps:**
1. Run deliberation with 10+ rounds
2. Monitor execution time
3. Check memory usage
4. Verify output quality

**Expected Result:** Handles many rounds efficiently

### Test 6.3: Long Case Testing
**Objective:** Test with very long case descriptions

**Steps:**
1. Create test case with 10,000+ characters
2. Run deliberation
3. Check processing time
4. Verify output quality

**Expected Result:** Handles long cases without issues

---

## Phase 7: Regression Testing

### Test 7.1: Feature Completeness
**Objective:** Verify all original features are preserved

**Steps:**
1. Compare feature list with original notebook
2. Test each feature systematically
3. Verify output format matches original
4. Check all configuration options

**Features to Verify:**
- Multi-round deliberations ✅
- Diverse jury personas ✅
- Multiple case scenarios ✅
- LLM flexibility ✅
- Structured output ✅
- Configurable jury size ✅
- Intermediate verdict tracking ✅

### Test 7.2: Output Quality Testing
**Objective:** Verify output quality matches original

**Steps:**
1. Run identical test case with both systems
2. Compare deliberation quality
3. Compare verdict accuracy
4. Compare output formatting

**Expected Result:** Output quality equivalent or better than original

---

## Phase 8: Documentation and Usability Testing

### Test 8.1: Documentation Testing
**Objective:** Verify all documentation is accurate

**Steps:**
1. Test all CLI examples in README
2. Verify setup instructions work
3. Test all code examples
4. Check for broken links or outdated information

**Expected Result:** All documentation examples work correctly

### Test 8.2: Usability Testing
**Objective:** Test user experience

**Steps:**
1. Have new user follow setup instructions
2. Test interactive mode usability
3. Verify error messages are helpful
4. Check help system completeness

**Expected Result:** Easy to use, clear instructions, helpful error messages

---

## Test Execution Schedule

### Day 1: Setup and Basic Testing
- Environment setup
- Import testing (Phase 1)
- Unit functionality testing (Phase 2)

### Day 2: CLI and Integration Testing
- CLI interface testing (Phase 3)
- Basic integration testing (Phase 4.1-4.2)

### Day 3: Advanced Integration and Error Testing
- Advanced integration testing (Phase 4.3-4.4)
- Error handling testing (Phase 5)

### Day 4: Performance and Regression Testing
- Performance testing (Phase 6)
- Regression testing (Phase 7)

### Day 5: Documentation and Final Validation
- Documentation testing (Phase 8)
- Final validation and cleanup

---

## Success Criteria

### Must Pass (Critical)
- All imports work without errors
- Basic CLI commands function
- End-to-end deliberation completes successfully
- All original features preserved
- Error handling works correctly

### Should Pass (Important)
- Interactive mode fully functional
- All jury configurations work
- Performance acceptable for typical use cases
- Documentation is accurate and helpful

### Nice to Have (Optional)
- Performance optimized for large juries
- Advanced error recovery
- Enhanced user experience features

---

## Test Results Tracking

For each test, document:
- **Test ID**: Unique identifier
- **Test Name**: Descriptive name
- **Status**: Pass/Fail/Skip
- **Result Details**: Specific outcomes
- **Issues Found**: Any problems discovered
- **Resolution**: How issues were resolved

## Conclusion

This comprehensive testing plan ensures that the refactored AI Agents Jury Deliberation system maintains all original functionality while providing improved usability, maintainability, and extensibility. The phased approach allows for systematic verification of each component and integration point.
