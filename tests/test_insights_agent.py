"""Unit tests for AI-powered insights agent."""

import unittest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from insights_agent import InsightsAgent
from experiment_manager import Experiment, SuccessCriteria, ComparisonOperator


class TestInsightsAgent(unittest.TestCase):
    """Test cases for InsightsAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock environment variable
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-123', 'OPENAI_MODEL': 'gpt-4o'}):
            self.agent = InsightsAgent()
        
        # Create sample experiments
        self.experiments = self._create_sample_experiments()
    
    def _create_sample_experiments(self):
        """Create sample experiment data for testing."""
        exp1 = Experiment(
            id='001',
            name='Title Length Test',
            hypothesis='Shorter titles will increase subscribers',
            start_date='2024-01-01',
            end_date='2024-01-07',
            metrics={'primary': 'subscriber_conversion'},
            success_criteria=SuccessCriteria(
                metric='subscriber_conversion',
                operator=ComparisonOperator.INCREASE,
                threshold=10.0
            )
        )
        exp1.results = {
            'success': True,
            'analysis_date': '2024-01-08',
            'metrics': {
                'subscriber_conversion': {
                    'treatment_value': 423,
                    'control_value': 127,
                    'change_percent': 233.1,
                    'treatment_vs_control': {
                        'change_percent': 233.1
                    }
                }
            }
        }
        
        exp2 = Experiment(
            id='002',
            name='Posting Frequency Test',
            hypothesis='2 posts per day will increase reach',
            start_date='2024-01-08',
            end_date='2024-01-14',
            metrics={'primary': 'views'},
            success_criteria=SuccessCriteria(
                metric='views',
                operator=ComparisonOperator.INCREASE,
                threshold=15.0
            )
        )
        exp2.results = {
            'success': True,
            'analysis_date': '2024-01-15',
            'metrics': {
                'views': {
                    'treatment_value': 15000,
                    'control_value': 8500,
                    'change_percent': 76.5,
                    'treatment_vs_control': {
                        'change_percent': 76.5
                    }
                }
            }
        }
        
        exp3 = Experiment(
            id='003',
            name='Thumbnail Style Test',
            hypothesis='AI-generated thumbnails will improve CTR',
            start_date='2024-01-15',
            end_date='2024-01-21',
            metrics={'primary': 'ctr'},
            success_criteria=SuccessCriteria(
                metric='ctr',
                operator=ComparisonOperator.INCREASE,
                threshold=10.0
            )
        )
        exp3.results = {
            'success': False,
            'analysis_date': '2024-01-22',
            'metrics': {
                'ctr': {
                    'treatment_value': 3.2,
                    'control_value': 4.8,
                    'change_percent': -33.3,
                    'treatment_vs_control': {
                        'change_percent': -33.3
                    }
                }
            }
        }
        
        return [exp1, exp2, exp3]
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-123', 'OPENAI_MODEL': 'gpt-4o'})
    def test_initialization(self):
        """Test agent initialization."""
        agent = InsightsAgent()
        self.assertEqual(agent.model, 'gpt-4o')
        self.assertEqual(agent.api_key, 'test-key-123')
        self.assertIsNotNone(agent.client)
        self.assertEqual(agent.cache, {})
    
    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key-123', 'OPENAI_MODEL': 'gpt-4o-mini'})
    def test_initialization_custom_model(self):
        """Test agent initialization with custom model."""
        agent = InsightsAgent()
        self.assertEqual(agent.model, 'gpt-4o-mini')
    
    def test_initialization_no_api_key(self):
        """Test that initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with self.assertRaises(ValueError) as context:
                InsightsAgent()
            self.assertIn('OPENAI_API_KEY', str(context.exception))
    
    def test_prepare_experiment_data(self):
        """Test experiment data preparation."""
        channel_info = {
            'channel_name': 'Test Channel',
            'niche': 'Education',
            'subscribers': 10000
        }
        
        data = self.agent._prepare_experiment_data(self.experiments, channel_info)
        
        # Check structure
        self.assertIn('channel', data)
        self.assertIn('experiments', data)
        self.assertIn('summary', data)
        
        # Check channel info
        self.assertEqual(data['channel'], channel_info)
        
        # Check experiments list
        self.assertEqual(len(data['experiments']), 3)
        
        # Check first experiment
        exp1_data = data['experiments'][0]
        self.assertEqual(exp1_data['id'], '001')
        self.assertEqual(exp1_data['name'], 'Title Length Test')
        self.assertTrue(exp1_data['success'])
        self.assertAlmostEqual(exp1_data['impact_percent'], 233.1, places=1)
        
        # Check summary
        summary = data['summary']
        self.assertEqual(summary['total_experiments'], 3)
        self.assertEqual(summary['successful'], 2)
        self.assertEqual(summary['failed'], 1)
        self.assertAlmostEqual(summary['success_rate'], 66.7, places=1)
    
    def test_prepare_experiment_data_no_results(self):
        """Test data preparation filters out experiments without results."""
        exp_no_results = Experiment(
            id='004',
            name='Incomplete Test',
            hypothesis='Test hypothesis',
            start_date='2024-01-22',
            end_date='2024-01-28',
            metrics={'primary': 'views'},
            success_criteria=SuccessCriteria(
                metric='views',
                operator=ComparisonOperator.INCREASE,
                threshold=10.0
            )
        )
        # No results set
        
        experiments = self.experiments + [exp_no_results]
        data = self.agent._prepare_experiment_data(experiments)
        
        # Should only include experiments with results
        self.assertEqual(len(data['experiments']), 3)
        self.assertEqual(data['summary']['total_experiments'], 3)
    
    def test_build_prompt(self):
        """Test prompt building with correct structure."""
        data = self.agent._prepare_experiment_data(self.experiments)
        prompt = self.agent._build_prompt(data)
        
        # Check key sections are present
        self.assertIn("You're an expert YouTube data analytics", prompt)
        self.assertIn("CONTEXT:", prompt)
        self.assertIn("EXPERIMENT DATA:", prompt)
        self.assertIn("TASK:", prompt)
        self.assertIn("JSON STRUCTURE:", prompt)
        self.assertIn("RULES:", prompt)
        self.assertIn("CALCULATIONS:", prompt)
        
        # Check data is included
        self.assertIn("Total experiments: 3", prompt)
        self.assertIn("Success rate: 66.7%", prompt)
        self.assertIn("Title Length Test (+233.1%)", prompt)
        
        # Check new prompt structure elements
        self.assertIn("proven_practices", prompt)
        self.assertIn("publishing_spec", prompt)
        self.assertIn("impact_ranking", prompt)
        self.assertIn("failed_practices", prompt)
        self.assertIn("next_experiments", prompt)
        self.assertIn("conflicts", prompt)
        self.assertIn("key_insight", prompt)
        
        # Check it includes experiment data as JSON
        self.assertIn('"id": "001"', prompt)
        self.assertIn('"name": "Title Length Test"', prompt)
    
    def test_build_prompt_no_best_result(self):
        """Test prompt building when no successful experiments."""
        exp_failed = Experiment(
            id='005',
            name='Failed Test',
            hypothesis='Test hypothesis',
            start_date='2024-01-01',
            end_date='2024-01-07',
            metrics={'primary': 'views'},
            success_criteria=SuccessCriteria(
                metric='views',
                operator=ComparisonOperator.INCREASE,
                threshold=10.0
            )
        )
        exp_failed.results = {
            'success': False,
            'analysis_date': '2024-01-08',
            'metrics': {
                'views': {
                    'change_percent': -10
                }
            }
        }
        
        data = self.agent._prepare_experiment_data([exp_failed])
        prompt = self.agent._build_prompt(data)
        
        self.assertIn("Best result: Not yet determined", prompt)
    
    @patch('insights_agent.OpenAI')
    def test_call_openai_success_json(self, mock_openai_class):
        """Test successful OpenAI API call with JSON response."""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_message = Mock()
        
        # Create a valid JSON response matching new structure
        json_response = {
            "proven_practices": [
                {
                    "element": "Title length",
                    "specification": "38-42 characters, front-load hook word",
                    "baseline_metric": "127 subs per video",
                    "test_metric": "423 subs per video",
                    "absolute_change": 296,
                    "percent_change": 233.1,
                    "experiment_ids": ["001"],
                    "sample_size": 1,
                    "confidence": "high",
                    "notes": "Strong positive result"
                }
            ],
            "publishing_spec": {
                "title": {
                    "length_chars": "38-42",
                    "length_words": "5-7",
                    "structure": "Hook + Context + #hashtag",
                    "keywords": "Front-loaded",
                    "hashtags_in_title": "1 at end"
                }
            },
            "impact_ranking": [],
            "failed_practices": [],
            "next_experiments": [],
            "conflicts": [],
            "key_insight": "Shorter, punchy titles drive 233% more subscriptions"
        }
        
        mock_message.content = json.dumps(json_response)
        mock_response.choices = [Mock(message=mock_message)]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Create agent with mocked client
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o'}):
            agent = InsightsAgent()
            agent.client = mock_client
        
        data = agent._prepare_experiment_data(self.experiments)
        result = agent._call_openai(data)
        
        # Check result structure
        self.assertIn('proven_practices', result)
        self.assertIn('publishing_spec', result)
        self.assertIn('generated_at', result)
        self.assertIn('model', result)
        self.assertEqual(result['model'], 'gpt-4o')
        
        # Verify the API was called correctly
        mock_client.chat.completions.create.assert_called_once()
        call_args = mock_client.chat.completions.create.call_args
        self.assertEqual(call_args.kwargs['model'], 'gpt-4o')
        self.assertEqual(call_args.kwargs['temperature'], 0.7)
    
    @patch('insights_agent.OpenAI')
    def test_call_openai_success_text(self, mock_openai_class):
        """Test OpenAI API call with text (non-JSON) response."""
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = "Here are some insights based on your experiments..."
        mock_response.choices = [Mock(message=mock_message)]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o'}):
            agent = InsightsAgent()
            agent.client = mock_client
        
        data = agent._prepare_experiment_data(self.experiments)
        result = agent._call_openai(data)
        
        # Should structure text response
        self.assertIn('narrative', result)
        self.assertIn('generated_at', result)
        self.assertIn('model', result)
    
    @patch('insights_agent.OpenAI')
    def test_call_openai_error(self, mock_openai_class):
        """Test OpenAI API call error handling."""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o'}):
            agent = InsightsAgent()
            agent.client = mock_client
        
        data = agent._prepare_experiment_data(self.experiments)
        result = agent._call_openai(data)
        
        # Should return error structure
        self.assertIn('error', result)
        self.assertIn('message', result)
        self.assertIn('API Error', result['error'])
    
    @patch('insights_agent.OpenAI')
    def test_generate_insights_with_cache(self, mock_openai_class):
        """Test insights generation uses cache."""
        # Mock successful response
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps({
            "proven_practices": [],
            "publishing_spec": {},
            "impact_ranking": [],
            "failed_practices": [],
            "next_experiments": [],
            "conflicts": [],
            "key_insight": "Test insight"
        })
        mock_response.choices = [Mock(message=mock_message)]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o'}):
            agent = InsightsAgent()
            agent.client = mock_client
        
        # First call - should hit API
        result1 = agent.generate_insights(self.experiments)
        self.assertEqual(mock_client.chat.completions.create.call_count, 1)
        
        # Second call - should use cache
        result2 = agent.generate_insights(self.experiments)
        self.assertEqual(mock_client.chat.completions.create.call_count, 1)  # No additional call
        
        # Results should be the same
        self.assertEqual(result1, result2)
    
    @patch('insights_agent.OpenAI')
    def test_generate_insights_cache_expiry(self, mock_openai_class):
        """Test cache expiry after timeout."""
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps({
            "proven_practices": [],
            "publishing_spec": {},
            "impact_ranking": [],
            "failed_practices": [],
            "next_experiments": [],
            "conflicts": [],
            "key_insight": "Test insight"
        })
        mock_response.choices = [Mock(message=mock_message)]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o'}):
            agent = InsightsAgent()
            agent.client = mock_client
            agent.cache_duration = 1  # 1 second cache
        
        # First call
        agent.generate_insights(self.experiments)
        self.assertEqual(mock_client.chat.completions.create.call_count, 1)
        
        # Wait for cache to expire
        import time
        time.sleep(1.5)
        
        # Second call - cache expired, should hit API again
        agent.generate_insights(self.experiments)
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
    
    def test_clear_cache(self):
        """Test cache clearing."""
        self.agent.cache = {'key1': 'value1', 'key2': 'value2'}
        self.assertEqual(len(self.agent.cache), 2)
        
        self.agent.clear_cache()
        self.assertEqual(len(self.agent.cache), 0)
    
    def test_get_latest_analysis_date(self):
        """Test getting the latest analysis date from experiments."""
        date = self.agent._get_latest_analysis_date(self.experiments)
        self.assertEqual(date, '2024-01-22')  # Latest date from exp3
    
    def test_get_latest_analysis_date_empty(self):
        """Test getting analysis date with no analyzed experiments."""
        exp_no_results = Experiment(
            id='999',
            name='Test',
            hypothesis='Test',
            start_date='2024-01-01',
            end_date='2024-01-07',
            metrics={'primary': 'views'},
            success_criteria=SuccessCriteria(
                metric='views',
                operator=ComparisonOperator.INCREASE,
                threshold=10.0
            )
        )
        
        date = self.agent._get_latest_analysis_date([exp_no_results])
        # Should return current date as ISO string
        self.assertIsInstance(date, str)
        # Check if it's a valid ISO format date
        try:
            datetime.fromisoformat(date)
            date_valid = True
        except:
            date_valid = False
        self.assertTrue(date_valid, "Date should be in ISO format")


class TestInsightsAgentIntegration(unittest.TestCase):
    """Integration tests for InsightsAgent."""
    
    @patch('insights_agent.OpenAI')
    def test_full_insights_generation_flow(self, mock_openai_class):
        """Test complete flow from experiments to insights."""
        # Create realistic mock response
        mock_response = Mock()
        mock_message = Mock()
        mock_message.content = json.dumps({
            "proven_practices": [
                {
                    "element": "Title length",
                    "specification": "5-7 words, 38-42 characters",
                    "baseline_metric": "127 subs",
                    "test_metric": "423 subs",
                    "absolute_change": 296,
                    "percent_change": 233.1,
                    "experiment_ids": ["001"],
                    "sample_size": 1,
                    "confidence": "high",
                    "notes": "Strong result"
                }
            ],
            "publishing_spec": {
                "title": {
                    "length_chars": "38-42",
                    "length_words": "5-7",
                    "structure": "Hook + Context",
                    "keywords": "Front-loaded",
                    "hashtags_in_title": "1"
                },
                "hashtags": {
                    "total_count": "3-5",
                    "placement": "caption",
                    "types": "mix",
                    "examples": ["#shorts", "#viral"]
                },
                "thumbnail": {
                    "style": "simple",
                    "text_overlay": "minimal",
                    "key_elements": ["face", "text"],
                    "avoid": ["clutter"]
                },
                "posting": {
                    "frequency": "2 per day",
                    "timing": "9 AM, 7 PM JST",
                    "gaps": "10 hours"
                },
                "video": {
                    "length_seconds": "15-30",
                    "hook_timing": "first 2 seconds",
                    "other_specs": "fast pace"
                }
            },
            "impact_ranking": [
                {
                    "rank": 1,
                    "practice": "Title optimization",
                    "metric_moved": "subscribers",
                    "baseline": "127",
                    "result": "423",
                    "percent_gain": 233.1,
                    "experiment_id": "001",
                    "reliability": "high"
                }
            ],
            "failed_practices": [],
            "next_experiments": [
                {
                    "id": "004",
                    "variable": "Upload timing",
                    "hypothesis": "Evening posts get 30% more views",
                    "test_design": "9 AM vs 7 PM upload",
                    "expected_impact": "20-30%",
                    "priority": "high",
                    "rationale": "Compound title success",
                    "success_metric": "views"
                }
            ],
            "conflicts": [],
            "key_insight": "Title length optimization drives 233% subscriber growth"
        })
        mock_response.choices = [Mock(message=mock_message)]
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client
        
        # Create agent and experiments
        with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key', 'OPENAI_MODEL': 'gpt-4o'}):
            agent = InsightsAgent()
            agent.client = mock_client
        
        exp = Experiment(
            id='001',
            name='Title Test',
            hypothesis='Short titles work better',
            start_date='2024-01-01',
            end_date='2024-01-07',
            metrics={'primary': 'subscribers'},
            success_criteria=SuccessCriteria(
                metric='subscribers',
                operator=ComparisonOperator.INCREASE,
                threshold=10.0
            )
        )
        exp.results = {
            'success': True,
            'analysis_date': '2024-01-08',
            'metrics': {
                'subscribers': {
                    'change_percent': 233.1
                }
            }
        }
        
        # Generate insights
        channel_info = {'channel_name': 'Test Channel'}
        insights = agent.generate_insights([exp], channel_info)
        
        # Verify complete structure
        self.assertIn('proven_practices', insights)
        self.assertIn('publishing_spec', insights)
        self.assertIn('impact_ranking', insights)
        self.assertIn('next_experiments', insights)
        self.assertIn('key_insight', insights)
        self.assertIn('generated_at', insights)
        self.assertIn('model', insights)
        
        # Verify content quality
        self.assertGreater(len(insights['proven_practices']), 0)
        self.assertIn('title', insights['publishing_spec'])
        self.assertEqual(insights['model'], 'gpt-4o')


if __name__ == '__main__':
    unittest.main()

