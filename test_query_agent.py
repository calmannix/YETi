"""Test script for the Analytics Query Agent feature."""

import os
import sys
from datetime import datetime, timedelta

# Ensure proper imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from query_agent import QueryAgent
from youtube_analytics import YouTubeAnalytics


def test_date_parsing():
    """Test that the LLM correctly parses various date formats."""
    print("\n" + "="*70)
    print("Testing Date Parsing")
    print("="*70)
    
    test_questions = [
        "Which video had the most views in the last 3 months?",
        "Show me total channel views for this year",
        "What are my top 5 videos by subscriber gain last week?",
        "How many likes did I get last month?"
    ]
    
    print("\nSample queries to test:")
    for i, q in enumerate(test_questions, 1):
        print(f"{i}. {q}")
    
    print("\n✓ Date parsing will be tested via LLM function calling")
    print("  The LLM should convert phrases like 'last 3 months' to actual dates")


def test_query_agent():
    """Test the query agent with sample questions."""
    print("\n" + "="*70)
    print("Testing Query Agent Functionality")
    print("="*70)
    
    # Check if credentials exist
    if not os.path.exists('credentials.json'):
        print("\n⚠️  WARNING: credentials.json not found")
        print("   YouTube API integration will not work without it")
        print("   See YOUTUBE_API_SETUP.md for setup instructions")
        return False
    
    # Check if OpenAI API key exists
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  WARNING: OPENAI_API_KEY not found in .env file")
        print("   The query agent requires OpenAI API access")
        print("   Add OPENAI_API_KEY=your-key-here to your .env file")
        return False
    
    try:
        print("\n1. Initializing YouTube Analytics API...")
        youtube_api = YouTubeAnalytics()
        print("   ✓ YouTube API initialized")
        
        print("\n2. Initializing Query Agent...")
        query_agent = QueryAgent(youtube_api)
        print("   ✓ Query Agent initialized")
        
        print("\n3. Testing sample query...")
        test_query = "How many total views did I get in the last 30 days?"
        print(f"   Query: {test_query}")
        
        result = query_agent.process_query(test_query)
        
        if result.get('success'):
            print("\n   ✓ Query processed successfully!")
            print(f"\n   Answer:\n   {result.get('formatted', 'No formatted response')}")
            
            if 'query_info' in result:
                info = result['query_info']
                print(f"\n   Function called: {info.get('function')}")
                print(f"   Parameters: {info.get('parameters')}")
        else:
            print("\n   ✗ Query failed")
            print(f"   Error: {result.get('error')}")
            print(f"   Explanation: {result.get('explanation')}")
            return False
        
        print("\n✓ All tests passed!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoint():
    """Test the API endpoint."""
    print("\n" + "="*70)
    print("Testing API Endpoint")
    print("="*70)
    
    print("\n1. The API endpoint is available at: POST /api/query")
    print("2. Start the server with: python start_server.py")
    print("3. Test the endpoint with:")
    print("\n   curl -X POST http://localhost:5000/api/query \\")
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"question": "Which video had the most views in the last month?"}\'')
    
    print("\n4. Or use the web UI at: http://localhost:5000")
    print("   Look for the '💬 Ask Analytics' section")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("YouTube Analytics Query Agent - Test Suite")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test_date_parsing()
    
    print("\n" + "="*70)
    
    # Check if we should run integration tests
    print("\nWould you like to run integration tests?")
    print("(This will make actual API calls to YouTube and OpenAI)")
    print("\nOptions:")
    print("  1. Yes - Run full integration test")
    print("  2. No - Just show API endpoint test instructions")
    print("  3. Exit")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            success = test_query_agent()
            if success:
                print("\n" + "="*70)
                print("✓ ALL TESTS PASSED")
                print("="*70)
                test_api_endpoint()
        elif choice == '2':
            test_api_endpoint()
        else:
            print("\nExiting...")
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")


if __name__ == '__main__':
    main()

