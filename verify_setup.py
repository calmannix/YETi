#!/usr/bin/env python3
"""
Verification script to check YouTube API setup is complete and working.
Run this after completing the setup steps.
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_check(passed, message):
    """Print a check result."""
    symbol = "✓" if passed else "✗"
    status = "PASS" if passed else "FAIL"
    print(f"{symbol} [{status}] {message}")
    return passed


def check_file_exists(filepath, description):
    """Check if a file exists."""
    exists = os.path.exists(filepath)
    print_check(exists, f"{description}: {filepath}")
    return exists


def test_imports():
    """Test if required packages are installed."""
    print_header("Testing Required Packages")
    
    all_passed = True
    
    try:
        import google.auth
        print_check(True, "google-auth installed")
    except ImportError:
        print_check(False, "google-auth NOT installed - run: pip install google-auth")
        all_passed = False
    
    try:
        import google_auth_oauthlib
        print_check(True, "google-auth-oauthlib installed")
    except ImportError:
        print_check(False, "google-auth-oauthlib NOT installed - run: pip install google-auth-oauthlib")
        all_passed = False
    
    try:
        import googleapiclient
        print_check(True, "google-api-python-client installed")
    except ImportError:
        print_check(False, "google-api-python-client NOT installed - run: pip install google-api-python-client")
        all_passed = False
    
    try:
        import flask
        print_check(True, "flask installed")
    except ImportError:
        print_check(False, "flask NOT installed - run: pip install flask")
        all_passed = False
    
    return all_passed


def test_files():
    """Test if required files exist."""
    print_header("Checking Required Files")
    
    all_passed = True
    
    # Check credentials.json
    if not check_file_exists('credentials.json', 'OAuth credentials file'):
        all_passed = False
        print("  → Download from Google Cloud Console")
        print("  → See YOUTUBE_API_SETUP.md for instructions")
    
    # Check token.pickle (optional - created on first run)
    token_exists = check_file_exists('token.pickle', 'Authorization token')
    if not token_exists:
        print("  ℹ This is OK if you haven't run authorization yet")
    
    # Check key project files
    check_file_exists('youtube_analytics.py', 'YouTube Analytics module')
    check_file_exists('cli.py', 'CLI module')
    check_file_exists('experiment_manager.py', 'Experiment manager')
    
    return all_passed


def test_youtube_connection():
    """Test connection to YouTube API."""
    print_header("Testing YouTube API Connection")
    
    if not os.path.exists('credentials.json'):
        print_check(False, "Cannot test - credentials.json not found")
        print("  → Complete setup steps first")
        return False
    
    try:
        from youtube_analytics import YouTubeAnalytics
        
        print("Attempting to connect to YouTube API...")
        print("(This may open a browser window for authorization)")
        
        youtube = YouTubeAnalytics()
        print_check(True, "Successfully authenticated with YouTube API")
        
        # Try to get available metrics (doesn't require channel data)
        metrics = youtube.get_available_metrics()
        print_check(len(metrics) > 0, f"Retrieved {len(metrics)} available metrics")
        
        return True
        
    except FileNotFoundError as e:
        print_check(False, f"File not found: {e}")
        return False
    except Exception as e:
        print_check(False, f"Authentication failed: {str(e)}")
        print("\nTroubleshooting:")
        print("  1. Make sure credentials.json is valid")
        print("  2. Complete browser authorization if prompted")
        print("  3. Check that YouTube Analytics API is enabled")
        print("  4. See YOUTUBE_API_SETUP.md for help")
        return False


def test_channel_access():
    """Test if we can access channel data."""
    print_header("Testing Channel Access")
    
    try:
        from youtube_analytics import YouTubeAnalytics
        from datetime import datetime, timedelta
        
        youtube = YouTubeAnalytics()
        
        # Try to get recent analytics (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        print(f"Fetching channel data from {start_date.date()} to {end_date.date()}...")
        
        result = youtube.get_aggregate_metrics(
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            metrics=['views']
        )
        
        if result.get('data'):
            print_check(True, "Successfully retrieved channel analytics data")
            print(f"  → Found {result.get('row_count', 0)} data points")
            return True
        else:
            print_check(False, "No analytics data returned")
            print("  ℹ This may be normal if:")
            print("    - Your channel is new")
            print("    - You haven't uploaded videos recently")
            print("    - Analytics data isn't available yet (24-72 hour delay)")
            return True  # Not necessarily a failure
            
    except Exception as e:
        print_check(False, f"Failed to retrieve analytics: {str(e)}")
        print("\nPossible issues:")
        print("  1. Wrong YouTube account authenticated")
        print("  2. Channel doesn't have analytics enabled")
        print("  3. API permissions not granted correctly")
        return False


def print_summary(all_checks):
    """Print summary of all checks."""
    print_header("Setup Verification Summary")
    
    if all(all_checks):
        print("\n✓ ALL CHECKS PASSED!")
        print("\nYour YouTube API setup is complete and working correctly.")
        print("\nNext steps:")
        print("  1. Run: python start_server.py")
        print("  2. Open: http://localhost:5000")
        print("  3. Create your first experiment!")
        print("\nSee QUICKSTART_V2.md for usage guide.")
    else:
        print("\n✗ SOME CHECKS FAILED")
        print("\nPlease fix the issues above before proceeding.")
        print("See YOUTUBE_API_SETUP.md for detailed setup instructions.")
    
    print("\n" + "=" * 70 + "\n")


def main():
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("  YOUTUBE API SETUP VERIFICATION")
    print("  Checking if your setup is complete and working...")
    print("=" * 70)
    
    checks = []
    
    # Run tests
    checks.append(test_imports())
    checks.append(test_files())
    checks.append(test_youtube_connection())
    checks.append(test_channel_access())
    
    # Print summary
    print_summary(checks)
    
    # Exit with appropriate code
    sys.exit(0 if all(checks) else 1)


if __name__ == '__main__':
    main()

