#!/usr/bin/env python3
"""
Test runner for YouTube Experiment Manager v2.0

Runs all unit tests and generates a summary report.
"""

import sys
import unittest
import time
from io import StringIO


def run_all_tests():
    """Run all unit tests and display results."""
    
    print("="*70)
    print("YouTube Experiment Manager v2.0 - Unit Test Suite")
    print("="*70)
    print()
    
    # Discover and load all tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Count tests
    def count_tests(test_suite):
        count = 0
        for test in test_suite:
            if isinstance(test, unittest.TestSuite):
                count += count_tests(test)
            else:
                count += 1
        return count
    
    total_tests = count_tests(suite)
    print(f"Discovered {total_tests} tests")
    print()
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print()
    print("="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print(f"Time: {end_time - start_time:.2f} seconds")
    print()
    
    # Calculate success rate
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    # Show failures if any
    if result.failures:
        print("="*70)
        print("FAILURES")
        print("="*70)
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    # Show errors if any
    if result.errors:
        print("="*70)
        print("ERRORS")
        print("="*70)
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    # Final result
    print("="*70)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print("="*70)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("="*70)
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())





