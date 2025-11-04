#!/usr/bin/env python3
"""Comprehensive health check for YouTube Experiment system."""

import os
import sys
from pathlib import Path
from datetime import datetime

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_files():
    """Check for required files."""
    print_section("FILE CHECK")
    
    required_files = {
        '.env': 'OpenAI API key configuration',
        'credentials.json': 'YouTube API credentials',
        'experiments.yaml': 'Experiment data storage',
        'token.pickle': 'YouTube API authentication token'
    }
    
    results = {}
    for file, description in required_files.items():
        exists = os.path.exists(file)
        status = "✓ FOUND" if exists else "✗ MISSING"
        print(f"{status:12} {file:25} - {description}")
        results[file] = exists
    
    return results

def check_environment():
    """Check environment variables."""
    print_section("ENVIRONMENT VARIABLES")
    
    from dotenv import load_dotenv
    
    # Try to load .env file
    env_loaded = load_dotenv()
    print(f"{'✓' if env_loaded else '✗'} .env file loaded: {env_loaded}")
    
    # Check for OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"✓ OPENAI_API_KEY: Found ({openai_key[:20]}...)")
    else:
        print("✗ OPENAI_API_KEY: Not found")
    
    # Check model setting
    model = os.getenv('OPENAI_MODEL', 'gpt-4o')
    print(f"✓ OPENAI_MODEL: {model}")
    
    return bool(openai_key)

def check_experiments():
    """Check experiment data."""
    print_section("EXPERIMENT DATA")
    
    try:
        from experiment_manager import ExperimentManager
        
        manager = ExperimentManager()
        experiments = manager.list_experiments()
        
        print(f"✓ Total experiments: {len(experiments)}")
        
        completed = [e for e in experiments if e.results]
        print(f"✓ Analyzed experiments: {len(completed)}")
        
        active = [e for e in experiments if e.is_active()]
        print(f"✓ Active experiments: {len(active)}")
        
        ready = [e for e in experiments if e.is_ready_for_analysis()]
        print(f"✓ Ready for analysis: {len(ready)}")
        
        if experiments:
            latest = experiments[0]
            print(f"\n  Latest experiment:")
            print(f"    ID: {latest.id}")
            print(f"    Name: {latest.name}")
            print(f"    Status: {latest.status.value}")
            print(f"    Has results: {'Yes' if latest.results else 'No'}")
        
        return True
    except Exception as e:
        print(f"✗ Error loading experiments: {e}")
        return False

def check_youtube_api():
    """Check YouTube API connection."""
    print_section("YOUTUBE API")
    
    if not os.path.exists('credentials.json'):
        print("✗ credentials.json not found")
        print("\n  To fix this:")
        print("  1. Go to https://console.cloud.google.com")
        print("  2. Create/select a project")
        print("  3. Enable YouTube Analytics API and YouTube Data API v3")
        print("  4. Create OAuth 2.0 credentials")
        print("  5. Download credentials.json to this directory")
        return False
    
    print("✓ credentials.json found")
    
    # Check token
    if os.path.exists('token.pickle'):
        print("✓ token.pickle found (authentication saved)")
        
        # Try to use the API
        try:
            from youtube_analytics import YouTubeAnalytics
            print("\n  Testing YouTube API connection...")
            
            yt = YouTubeAnalytics()
            metrics = yt.get_available_metrics()
            print(f"✓ YouTube API connected successfully")
            print(f"  Available metrics: {len(metrics)}")
            return True
        except Exception as e:
            print(f"✗ YouTube API connection failed: {e}")
            print(f"\n  Error type: {type(e).__name__}")
            return False
    else:
        print("✗ token.pickle not found (need to authenticate)")
        print("\n  Run verify_setup.py to authenticate")
        return False

def check_insights_agent():
    """Check AI insights functionality."""
    print_section("AI INSIGHTS")
    
    try:
        from insights_agent import InsightsAgent
        
        agent = InsightsAgent()
        print(f"✓ InsightsAgent initialized")
        print(f"  Model: {agent.model}")
        print(f"  API key: {agent.api_key[:20]}..." if agent.api_key else "  API key: Not found")
        
        if not agent.api_key:
            print("\n✗ OpenAI API key not configured")
            return False
        
        return True
    except ValueError as e:
        print(f"✗ InsightsAgent initialization failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def check_api_server():
    """Check if API server can start."""
    print_section("API SERVER")
    
    try:
        # Import server modules
        from api.server import app, experiment_manager
        
        print("✓ Server modules imported successfully")
        print(f"✓ Experiment manager initialized")
        print(f"  Total experiments: {len(experiment_manager.experiments)}")
        
        # Test health endpoint
        with app.test_client() as client:
            response = client.get('/api/health')
            if response.status_code == 200:
                data = response.get_json()
                print(f"✓ Health endpoint responding")
                print(f"  Status: {data.get('status')}")
                print(f"  Version: {data.get('version')}")
            else:
                print(f"✗ Health endpoint failed: {response.status_code}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Server check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_report(results):
    """Generate summary report."""
    print_section("HEALTH CHECK SUMMARY")
    
    issues = []
    
    # Check each component
    if not results.get('files', {}).get('.env'):
        issues.append({
            'severity': 'HIGH',
            'component': 'Environment Config',
            'issue': '.env file missing',
            'fix': 'Create .env file from config_template.env: cp config_template.env .env'
        })
    
    if not results.get('files', {}).get('credentials.json'):
        issues.append({
            'severity': 'CRITICAL',
            'component': 'YouTube API',
            'issue': 'credentials.json missing',
            'fix': 'Set up YouTube API credentials (see YOUTUBE_API_SETUP.md)'
        })
    
    if not results.get('environment'):
        issues.append({
            'severity': 'HIGH',
            'component': 'AI Insights',
            'issue': 'OpenAI API key not configured',
            'fix': 'Add OPENAI_API_KEY to .env file'
        })
    
    if not results.get('youtube_api'):
        issues.append({
            'severity': 'CRITICAL',
            'component': 'YouTube Data',
            'issue': 'YouTube API not working',
            'fix': 'Complete YouTube API setup and authentication'
        })
    
    if not results.get('insights'):
        issues.append({
            'severity': 'MEDIUM',
            'component': 'AI Insights',
            'issue': 'AI insights agent not working',
            'fix': 'Ensure OPENAI_API_KEY is properly configured'
        })
    
    # Print issues
    if issues:
        print(f"\n🚨 Found {len(issues)} issue(s):\n")
        
        for i, issue in enumerate(issues, 1):
            print(f"{i}. [{issue['severity']}] {issue['component']}")
            print(f"   Issue: {issue['issue']}")
            print(f"   Fix: {issue['fix']}\n")
    else:
        print("\n✅ All systems operational!\n")
    
    # Overall status
    critical_issues = [i for i in issues if i['severity'] == 'CRITICAL']
    if critical_issues:
        print("⚠️  CRITICAL ISSUES PREVENT SYSTEM FROM WORKING")
        print("   Fix critical issues first before system can function.\n")
    elif issues:
        print("⚠️  SYSTEM PARTIALLY OPERATIONAL")
        print("   Some features may not work correctly.\n")
    else:
        print("✅ ALL SYSTEMS GO")
        print("   System is ready to use.\n")

def main():
    """Run comprehensive health check."""
    print("\n" + "=" * 70)
    print("  YOUTUBE EXPERIMENT SYSTEM - HEALTH CHECK")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    results = {}
    
    # Run checks
    results['files'] = check_files()
    results['environment'] = check_environment()
    results['experiments'] = check_experiments()
    results['youtube_api'] = check_youtube_api()
    results['insights'] = check_insights_agent()
    results['api_server'] = check_api_server()
    
    # Generate report
    generate_report(results)

if __name__ == '__main__':
    main()

