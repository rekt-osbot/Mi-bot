#!/usr/bin/env python3
"""
Test runner script for the Market Intelligence Bot.
Runs all tests and reports coverage.
"""

import unittest
import sys
import os
import logging

# Suppress logging during tests
logging.basicConfig(level=logging.CRITICAL)

# Try to import coverage if available
try:
    import coverage
    has_coverage = True
except ImportError:
    has_coverage = False
    print("Coverage module not found. Install with 'pip install coverage' for test coverage reporting.")

def run_tests_with_coverage():
    """Run tests with coverage reporting if available."""
    if has_coverage:
        # Start coverage measurement
        cov = coverage.Coverage(
            source=['src/marketbot'],
            omit=['*/tests/*', '*/migrations/*', '*/site-packages/*']
        )
        cov.start()
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    suite = loader.discover(start_dir, pattern="test_*.py")
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Report coverage if available
    if has_coverage:
        cov.stop()
        cov.save()
        print("\nCoverage Report:")
        cov.report()
        
        # Generate HTML report
        try:
            cov.html_report(directory='coverage_html')
            print(f"HTML coverage report generated in 'coverage_html' directory")
        except Exception as e:
            print(f"Error generating HTML coverage report: {e}")
    
    return result

def run_specific_test(test_file):
    """Run a specific test file."""
    if not test_file.endswith('.py'):
        test_file += '.py'
    
    if not os.path.exists(test_file):
        # Try to find it in the tests directory
        test_dir = os.path.dirname(os.path.abspath(__file__))
        potential_path = os.path.join(test_dir, test_file)
        if os.path.exists(potential_path):
            test_file = potential_path
        else:
            print(f"Test file {test_file} not found.")
            return False
    
    # Run the specific test file
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(test_file), pattern=os.path.basename(test_file))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    # If a specific test was specified, run just that one
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        success = run_specific_test(test_file)
        sys.exit(0 if success else 1)
    else:
        # Run all tests with coverage
        result = run_tests_with_coverage()
        # Return non-zero exit code if tests failed
        sys.exit(0 if result.wasSuccessful() else 1) 