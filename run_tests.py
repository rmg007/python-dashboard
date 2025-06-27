"""
Test runner for the Permit Dashboard application.
"""
import os
import sys
import pytest

def run_tests():
    """Run all tests in the tests directory."""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Set test environment variables
    os.environ['TESTING'] = 'True'
    
    # Run pytest
    test_dir = os.path.join(project_root, 'tests')
    return pytest.main([test_dir, '-v', '--cov=./', '--cov-report=term-missing'])

if __name__ == '__main__':
    sys.exit(run_tests())
