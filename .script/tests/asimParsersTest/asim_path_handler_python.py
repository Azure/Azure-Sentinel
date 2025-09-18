"""
Path Handler for ASim Parser Tests

This module provides path override functionality for ASim parser test scripts
to analyze code from different directories, supporting PR analysis workflows.

Usage:
    import asim_path_handler_python
    asim_path_handler_python.setup_secure_paths("/path/to/pr-code")
    # Now run your original script
"""

import os
import subprocess

# Global variable to store the source path
_source_path = None
_original_functions = {}

def setup_secure_paths(source_path=None):
    """
    Set up path overrides to analyze code from a different directory.
    
    Args:
        source_path (str): Path to the code directory to analyze. If None, uses standard behavior.
    """
    global _source_path
    _source_path = source_path
    
    if source_path and os.path.exists(source_path):
        print(f"� Using custom PR source path for testing: {source_path}")
        _patch_functions()
    else:
        print("📂 Testing ASim parsers from current repository")

def _patch_functions():
    """Patch os and subprocess functions to work with the secure path."""
    global _original_functions
    
    # Store original functions
    _original_functions['os_path_dirname'] = os.path.dirname
    _original_functions['subprocess_run'] = subprocess.run
    _original_functions['subprocess_check_output'] = subprocess.check_output
    
    # Override os.path.dirname for specific files
    def secure_dirname(path):
        if path and any(script in path for script in ['ASimFilteringTest.py', 'VerifyASimParserTemplate.py', 'ingestASimSampleData.py']):
            # Return the equivalent path in the source directory
            return os.path.join(_source_path, '.script', 'tests', 'asimParsersTest')
        return _original_functions['os_path_dirname'](path)
    
    # Override subprocess.run for git commands
    def secure_subprocess_run(command, **kwargs):
        if isinstance(command, str) and 'git diff --name-only upstream/master' in command:
            # Extract the current directory reference and replace with source path
            if '{current_directory}/../../../Parsers/' in command:
                modified_command = command.replace(
                    '{current_directory}/../../../Parsers/',
                    f'{_source_path}/Parsers/'
                )
                kwargs['cwd'] = _source_path
                return _original_functions['subprocess_run'](modified_command, **kwargs)
            # Handle cases where the path is constructed differently
            elif 'Parsers/' in command:
                kwargs['cwd'] = _source_path
        return _original_functions['subprocess_run'](command, **kwargs)
    
    # Override subprocess.check_output for git commands
    def secure_subprocess_check_output(command, **kwargs):
        if isinstance(command, str) and 'git diff --name-only upstream/master' in command:
            if 'Parsers/' in command:
                kwargs['cwd'] = _source_path
        return _original_functions['subprocess_check_output'](command, **kwargs)
    
    # Apply the patches
    os.path.dirname = secure_dirname
    subprocess.run = secure_subprocess_run
    subprocess.check_output = secure_subprocess_check_output

def restore_original_functions():
    """Restore original function behavior."""
    if _original_functions:
        os.path.dirname = _original_functions['os_path_dirname']
        subprocess.run = _original_functions['subprocess_run']
        subprocess.check_output = _original_functions['subprocess_check_output']

def get_secure_parser_path():
    """Get the correct path to the Parsers directory based on current mode."""
    if _source_path:
        return os.path.join(_source_path, 'Parsers')
    else:
        # Standard relative path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(current_dir, '..', '..', '..', 'Parsers')

def setup_git_environment():
    """Set up git environment for the source path when analyzing external code."""
    if _source_path and os.path.exists(_source_path):
        # Change to source directory and ensure upstream remote exists
        original_cwd = os.getcwd()
        try:
            os.chdir(_source_path)
            
            # Check if upstream remote exists
            result = subprocess.run(['git', 'remote'], capture_output=True, text=True)
            if 'upstream' not in result.stdout:
                subprocess.run(['git', 'remote', 'add', 'upstream', 'https://github.com/Azure/Azure-Sentinel.git'], check=True)
            
            # Fetch upstream
            subprocess.run(['git', 'fetch', 'upstream'], capture_output=True, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"Warning: Git setup failed: {e}")
        finally:
            os.chdir(original_cwd)

# Auto-setup if SOURCE_PATH environment variable is set
if __name__ == "__main__":
    source_path = os.environ.get('ASIM_SOURCE_PATH')
    if source_path:
        setup_secure_paths(source_path)