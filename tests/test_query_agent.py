"""Unit tests for Analytics Query Agent."""

import os
import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from query_agent import QueryAgent


class TestQueryAgent(unittest.TestCase):
    """Test cases for QueryAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock YouTube API
        self.mock_youtube_api = Mock()
        
        # Initialize agent with mocked dependencies
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-123', 'OPENAI_MODEL': 'gpt-4o'}):
            self.agent = QueryAgent(self.mock_youtube_api)
    
    def test_initialization(self):
        """Test QueryAgent initialization."""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.model, 'gpt-4o')
        self.assertEqual(self.agent.api_key, 'test-key-123')
        self.assertIs(self.agent.youtube_api, self.mock_youtube_api)
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict('os.environ', {'OPENAI_API_KEY': ''}, clear=True):
            with self.assertRaises(ValueError) as context:
                QueryAgent(self.mock_youtube_api)
            self.assertIn('OPENAI_API_KEY', str(context.exception))
    
    @patch('query_agent.QueryAgent._parse_query_with_llm')
    @patch('query_agent.QueryAgent._execute_query')
    @patch('query_agent.QueryAgent._format_results')
    def test_process_query_success(self, mock_format, mock_execute, mock_parse):
        """Test successful query processing."""
        # Mock the pipeline
        mock_parse.return_value = {
            'function': 'get_video_performance',
            'parameters': {
                'start_date': '2024-10-01',
                'end_date': '2024-10-31',
                'metrics': ['views'],
                'sort_by': 'views',
                'limit': 10
            },
            'original_question': 'Which video had the most views in October?'
        }
        
        mock_execute.return_value = {
            'type': 'video_performance',
            'videos': [
                {
                    'video_id': 'abc123',
                    'title': 'Test Video',
                    'views': 10000
                }
            ],
            'total_videos': 1,
            'date_range': {'start': '2024-10-01', 'end': '2024-10-31'},
            'metrics': ['views']
        }
        
        mock_format.return_value = 'Test Video had 10,000 views in October.'
        
        result = self.agent.process_query('Which video had the most views in October?')
        
        self.assertTrue(result['success'])
        self.assertIn('formatted', result)
        self.assertIn('data', result)
        self.assertIn('query_info', result)
        mock_parse.assert_called_once()
        mock_execute.assert_called_once()
        mock_format.assert_called_once()
    
    @patch('query_agent.QueryAgent._parse_query_with_llm')
    def test_process_query_parse_error(self, mock_parse):
        """Test query processing when parsing fails."""
        mock_parse.return_value = {
            'error': 'query_not_understood',
            'explanation': 'Could not understand the query'
        }
        
        result = self.agent.process_query('Invalid query')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'query_not_understood')
    
    @patch('query_agent.QueryAgent._parse_query_with_llm')
    @patch('query_agent.QueryAgent._execute_query')
    def test_process_query_execution_error(self, mock_execute, mock_parse):
        """Test query processing when execution fails."""
        mock_parse.return_value = {
            'function': 'get_video_performance',
            'parameters': {},
            'original_question': 'test'
        }
        
        mock_execute.return_value = {
            'error': 'api_error',
            'explanation': 'YouTube API error'
        }
        
        result = self.agent.process_query('test')
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    @patch('query_agent.OpenAI')
    def test_parse_query_with_llm_video_performance(self, mock_openai):
        """Test LLM query parsing for video performance queries."""
        # Mock OpenAI response
        mock_completion = Mock()
        mock_message = Mock()
        mock_tool_call = Mock()
        mock_function = Mock()
        
        mock_function.name = 'get_video_performance'
        mock_function.arguments = json.dumps({
            'start_date': '2024-08-01',
            'end_date': '2024-10-31',
            'metrics': ['views'],
            'sort_by': 'views',
            'limit': 1
        })
        
        mock_tool_call.function = mock_function
        mock_message.tool_calls = [mock_tool_call]
        mock_completion.choices = [Mock(message=mock_message)]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        # Reinitialize with mocked OpenAI
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o'}):
            agent = QueryAgent(self.mock_youtube_api)
            agent.client = mock_client
        
        result = agent._parse_query_with_llm('Which video had the most views in the last 3 months?')
        
        self.assertEqual(result['function'], 'get_video_performance')
        self.assertIn('parameters', result)
        self.assertIn('start_date', result['parameters'])
        self.assertIn('metrics', result['parameters'])
    
    @patch('query_agent.OpenAI')
    def test_parse_query_with_llm_aggregate_stats(self, mock_openai):
        """Test LLM query parsing for aggregate statistics."""
        # Mock OpenAI response
        mock_completion = Mock()
        mock_message = Mock()
        mock_tool_call = Mock()
        mock_function = Mock()
        
        mock_function.name = 'get_aggregate_stats'
        mock_function.arguments = json.dumps({
            'start_date': '2024-01-01',
            'end_date': '2024-10-31',
            'metrics': ['views', 'likes']
        })
        
        mock_tool_call.function = mock_function
        mock_message.tool_calls = [mock_tool_call]
        mock_completion.choices = [Mock(message=mock_message)]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o'}):
            agent = QueryAgent(self.mock_youtube_api)
            agent.client = mock_client
        
        result = agent._parse_query_with_llm('Total views this year')
        
        self.assertEqual(result['function'], 'get_aggregate_stats')
        self.assertIn('parameters', result)
    
    @patch('query_agent.OpenAI')
    def test_parse_query_with_llm_no_function_called(self, mock_openai):
        """Test LLM query parsing when no function is called."""
        mock_completion = Mock()
        mock_message = Mock()
        mock_message.tool_calls = None
        mock_message.content = 'I cannot understand that query'
        mock_completion.choices = [Mock(message=mock_message)]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o'}):
            agent = QueryAgent(self.mock_youtube_api)
            agent.client = mock_client
        
        result = agent._parse_query_with_llm('Invalid query')
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'query_not_understood')
    
    def test_execute_query_video_performance(self):
        """Test executing a video performance query."""
        parsed_query = {
            'function': 'get_video_performance',
            'parameters': {
                'start_date': '2024-10-01',
                'end_date': '2024-10-31',
                'metrics': ['views', 'likes'],
                'sort_by': 'views',
                'limit': 5
            }
        }
        
        # Mock YouTube API responses
        self.mock_youtube_api.get_channel_videos_by_date_range.return_value = [
            {'video_id': 'vid1', 'title': 'Video 1', 'published_at': '2024-10-01'},
            {'video_id': 'vid2', 'title': 'Video 2', 'published_at': '2024-10-15'}
        ]
        
        self.mock_youtube_api.get_video_metrics.return_value = {
            'data': [
                {'video': 'vid1', 'views': 1000, 'likes': 100},
                {'video': 'vid2', 'views': 500, 'likes': 50}
            ]
        }
        
        result = self.agent._execute_query(parsed_query)
        
        self.assertEqual(result['type'], 'video_performance')
        self.assertIn('videos', result)
        self.assertEqual(len(result['videos']), 2)
        self.assertEqual(result['videos'][0]['title'], 'Video 1')
        self.assertEqual(result['videos'][0]['views'], 1000)
    
    def test_execute_query_aggregate_stats(self):
        """Test executing an aggregate statistics query."""
        parsed_query = {
            'function': 'get_aggregate_stats',
            'parameters': {
                'start_date': '2024-01-01',
                'end_date': '2024-10-31',
                'metrics': ['views', 'likes', 'comments']
            }
        }
        
        # Mock YouTube API response
        self.mock_youtube_api.get_aggregate_metrics.return_value = {
            'data': [
                {'views': 100000, 'likes': 5000, 'comments': 500}
            ]
        }
        
        result = self.agent._execute_query(parsed_query)
        
        self.assertEqual(result['type'], 'aggregate_stats')
        self.assertIn('statistics', result)
        self.assertEqual(result['statistics']['views'], 100000)
        self.assertEqual(result['statistics']['likes'], 5000)
    
    def test_execute_query_unknown_function(self):
        """Test executing an unknown function."""
        parsed_query = {
            'function': 'unknown_function',
            'parameters': {}
        }
        
        result = self.agent._execute_query(parsed_query)
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'unknown_function')
    
    def test_get_video_performance_no_videos_found(self):
        """Test video performance query when no videos exist."""
        self.mock_youtube_api.get_channel_videos_by_date_range.return_value = []
        
        params = {
            'start_date': '2024-10-01',
            'end_date': '2024-10-31',
            'metrics': ['views'],
            'sort_by': 'views',
            'limit': 10
        }
        
        result = self.agent._get_video_performance(params)
        
        self.assertIn('error', result)
        self.assertEqual(result['error'], 'no_videos_found')
    
    def test_get_video_performance_with_sorting(self):
        """Test video performance query with sorting."""
        self.mock_youtube_api.get_channel_videos_by_date_range.return_value = [
            {'video_id': 'vid1', 'title': 'Video 1', 'published_at': '2024-10-01'},
            {'video_id': 'vid2', 'title': 'Video 2', 'published_at': '2024-10-15'},
            {'video_id': 'vid3', 'title': 'Video 3', 'published_at': '2024-10-20'}
        ]
        
        self.mock_youtube_api.get_video_metrics.return_value = {
            'data': [
                {'video': 'vid1', 'views': 500},
                {'video': 'vid2', 'views': 1500},
                {'video': 'vid3', 'views': 1000}
            ]
        }
        
        params = {
            'start_date': '2024-10-01',
            'end_date': '2024-10-31',
            'metrics': ['views'],
            'sort_by': 'views',
            'limit': 2
        }
        
        result = self.agent._get_video_performance(params)
        
        # Should be sorted by views descending and limited to 2
        self.assertEqual(len(result['videos']), 2)
        self.assertEqual(result['videos'][0]['views'], 1500)  # Highest first
        self.assertEqual(result['videos'][1]['views'], 1000)  # Second highest
    
    def test_get_aggregate_stats(self):
        """Test aggregate statistics retrieval."""
        self.mock_youtube_api.get_aggregate_metrics.return_value = {
            'data': [
                {'views': 50000, 'likes': 2500, 'comments': 300}
            ]
        }
        
        params = {
            'start_date': '2024-10-01',
            'end_date': '2024-10-31',
            'metrics': ['views', 'likes', 'comments']
        }
        
        result = self.agent._get_aggregate_stats(params)
        
        self.assertEqual(result['type'], 'aggregate_stats')
        self.assertEqual(result['statistics']['views'], 50000)
        self.assertIn('date_range', result)
    
    @patch('query_agent.OpenAI')
    def test_format_results(self, mock_openai):
        """Test formatting results with LLM."""
        mock_completion = Mock()
        mock_message = Mock()
        mock_message.content = 'Your top video was "Test Video" with 10,000 views.'
        mock_completion.choices = [Mock(message=mock_message)]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_completion
        
        self.agent.client = mock_client
        
        question = 'Which video had the most views?'
        parsed_query = {'function': 'get_video_performance'}
        raw_data = {
            'type': 'video_performance',
            'videos': [{'title': 'Test Video', 'views': 10000}]
        }
        
        result = self.agent._format_results(question, parsed_query, raw_data)
        
        self.assertIsInstance(result, str)
        self.assertIn('Test Video', result)
    
    def test_basic_format_video_performance(self):
        """Test basic formatting fallback for video performance."""
        raw_data = {
            'type': 'video_performance',
            'videos': [
                {'title': 'Video 1', 'views': 1000, 'likes': 100},
                {'title': 'Video 2', 'views': 500, 'likes': 50}
            ]
        }
        
        result = self.agent._basic_format(raw_data)
        
        self.assertIn('Video 1', result)
        self.assertIn('Video 2', result)
        self.assertIn('views', result.lower())
    
    def test_basic_format_aggregate_stats(self):
        """Test basic formatting fallback for aggregate statistics."""
        raw_data = {
            'type': 'aggregate_stats',
            'statistics': {
                'views': 100000,
                'likes': 5000,
                'comments': 500
            }
        }
        
        result = self.agent._basic_format(raw_data)
        
        self.assertIn('100,000', result)
        self.assertIn('5,000', result)
        self.assertIn('views', result.lower())
    
    def test_basic_format_empty_videos(self):
        """Test basic formatting with no videos."""
        raw_data = {
            'type': 'video_performance',
            'videos': []
        }
        
        result = self.agent._basic_format(raw_data)
        
        self.assertIn('No videos found', result)
    
    def test_basic_format_empty_stats(self):
        """Test basic formatting with no statistics."""
        raw_data = {
            'type': 'aggregate_stats',
            'statistics': {}
        }
        
        result = self.agent._basic_format(raw_data)
        
        self.assertIn('No statistics found', result)


class TestQueryAgentIntegration(unittest.TestCase):
    """Integration tests for QueryAgent (require API keys)."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        self.has_openai_key = bool(os.getenv('OPENAI_API_KEY'))
        self.has_youtube_credentials = os.path.exists('credentials.json')
    
    @unittest.skipUnless(
        os.getenv('RUN_INTEGRATION_TESTS') == '1',
        "Integration tests disabled. Set RUN_INTEGRATION_TESTS=1 to enable"
    )
    def test_full_query_flow(self):
        """Test full query flow with real APIs (requires credentials)."""
        if not self.has_openai_key or not self.has_youtube_credentials:
            self.skipTest("Missing API credentials")
        
        from youtube_analytics import YouTubeAnalytics
        
        youtube_api = YouTubeAnalytics()
        agent = QueryAgent(youtube_api)
        
        result = agent.process_query("How many total views did I get in the last 30 days?")
        
        self.assertTrue(result.get('success'), f"Query failed: {result.get('error')}")
        self.assertIn('formatted', result)


if __name__ == '__main__':
    unittest.main()

