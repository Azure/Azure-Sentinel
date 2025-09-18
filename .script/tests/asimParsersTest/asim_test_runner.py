#!/usr/bin/env python3
"""
ASim Parser Test Runner

A test runner for ASim parser validation scripts. This runner supports testing parser changes 
from different source directories and can execute filtering tests, template verification, and 
sample data ingestion with proper path handling for PR analysis workflows.

Usage:
    python asim_test_runner.py ASimFilteringTest --source-path "./pr-code"
    python asim_test_runner.py VerifyASimParserTemplate --source-path "./pr-code" 
    python asim_test_runner.py ingestASimSampleData --source-path "./pr-code"
"""

import sys
import os
import argparse
import importlib

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    parser = argparse.ArgumentParser(description='ASim Parser Test Runner - Execute ASim test scripts with PR analysis support')
    parser.add_argument('script_name', 
                        help='Name of the script to run (without .py extension)',
                        choices=['ASimFilteringTest', 'VerifyASimParserTemplate', 'ingestASimSampleData'])
    parser.add_argument('--source-path', 
                        help='Path to the source code directory to analyze',
                        default=None)
    # Forward any additional arguments to the original script
    parser.add_argument('additional_args', nargs='*', 
                        help='Additional arguments to pass to the original script')
    
    args = parser.parse_args()
    
    # Set up path handling
    import asim_path_handler_python
    asim_path_handler_python.setup_secure_paths(args.source_path)
    asim_path_handler_python.setup_git_environment()
    
    try:
        # If there are additional arguments, modify sys.argv to pass them through
        if args.additional_args:
            sys.argv = [args.script_name + '.py'] + args.additional_args
        
        # For scripts that run directly (like ingestASimSampleData.py), 
        # we need to execute them rather than import them
        if args.script_name == 'ingestASimSampleData':
            # Execute the script directly
            script_path = os.path.join(current_dir, f"{args.script_name}.py")
            exec(compile(open(script_path).read(), script_path, 'exec'))
        else:
            # Dynamically import and run the original script
            module = importlib.import_module(args.script_name)
            
            # Try to call the main function first, then run function as fallback
            if hasattr(module, 'main'):
                module.main()
            elif hasattr(module, 'run'):
                module.run()
            else:
                raise AttributeError(f"No main() or run() function found in {args.script_name}")
        
    except AttributeError as e:
        print(f"Error: {args.script_name}.py doesn't have a main() or run() function: {e}")
        return 1
    except ImportError as e:
        print(f"Error: Could not import {args.script_name}.py: {e}")
        return 1
    finally:
        # Restore original functions
        asim_path_handler_python.restore_original_functions()
    
    return 0

if __name__ == '__main__':
    sys.exit(main())