import pytest
import sys
import os

def run_tests():
    """Run all tests for the SEO Analyzer Service."""
    
    # Add the service directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest
    pytest_args = [
        "tests",
        "-v",  # Verbose output
        "--cov=analyzers",  # Coverage for analyzers module
        "--cov-report=html",  # Generate HTML coverage report
    ]
    
    exit_code = pytest.main(pytest_args)
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed.")
    
    return exit_code

if __name__ == "__main__":
    run_tests()