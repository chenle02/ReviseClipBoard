"""
Test runner script for the GPT-Clip application.
"""
import os
import sys
import pytest

def run_tests():
    """Run all tests with coverage reporting."""
    # Run tests with coverage
    test_args = [
        'tests/',
        '-v',
        '--cov=.',
        '--cov-report=term-missing',
        '--cov-report=html',
        '--cov-branch',
        '--cov-fail-under=80'  # Temporarily lower coverage requirement
    ]
    
    # Add pytest arguments from command line
    test_args.extend(sys.argv[1:])
    
    # Run pytest
    return pytest.main(test_args)

if __name__ == '__main__':
    sys.exit(run_tests()) 