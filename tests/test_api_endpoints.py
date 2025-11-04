"""Unit tests for Flask API endpoints."""

import unittest
import json
from api.server import app


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['version'], '2.0.0')
        self.assertIn('timestamp', data)
    
    def test_home_page(self):
        """Test dashboard home page."""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        self.assertIn(b'YouTube Experiment Manager', response.data)
    
    def test_list_experiments(self):
        """Test listing experiments."""
        response = self.client.get('/api/experiments')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('experiments', data)
        self.assertIn('count', data)
        self.assertIsInstance(data['experiments'], list)
    
    def test_list_experiments_with_filter(self):
        """Test listing experiments with status filter."""
        response = self.client.get('/api/experiments?status=active')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('experiments', data)
    
    def test_get_experiment_not_found(self):
        """Test getting non-existent experiment."""
        response = self.client.get('/api/experiments/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_dashboard_summary(self):
        """Test dashboard summary endpoint."""
        response = self.client.get('/api/dashboard/summary')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check all expected fields
        self.assertIn('total_experiments', data)
        self.assertIn('active', data)
        self.assertIn('completed', data)
        self.assertIn('successful', data)
        self.assertIn('success_rate', data)
        self.assertIn('ready_for_analysis', data)
        self.assertIn('recent_experiments', data)
    
    def test_get_next_experiment_id(self):
        """Test getting next sequential experiment ID."""
        response = self.client.get('/api/experiments/next-id')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('next_id', data)
        self.assertIsInstance(data['next_id'], str)
        # Should be a numeric string
        self.assertTrue(data['next_id'].isdigit())
    
    def test_calculate_sample_size(self):
        """Test sample size calculation endpoint."""
        response = self.client.post('/api/statistics/sample-size',
            json={
                'baseline_rate': 0.05,
                'expected_lift': 0.20,
                'power': 0.80
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('sample_size_per_variant', data)
        self.assertIn('total_sample_size', data)
        self.assertGreater(data['sample_size_per_variant'], 0)
    
    def test_calculate_significance(self):
        """Test significance calculation endpoint."""
        response = self.client.post('/api/statistics/significance',
            json={
                'control': {'successes': 100, 'total': 1000},
                'treatment': {'successes': 150, 'total': 1000},
                'metric_type': 'rate',
                'confidence_level': 0.95
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('is_significant', data)
        self.assertIn('p_value', data)
        self.assertIn('effect_size', data)
        self.assertIn('conclusion', data)
    
    def test_404_error_handler(self):
        """Test 404 error handling."""
        response = self.client.get('/api/nonexistent/endpoint')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)


class TestAPIContentTypes(unittest.TestCase):
    """Test API content types and headers."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_json_response_content_type(self):
        """Test that JSON endpoints return correct content type."""
        response = self.client.get('/api/health')
        self.assertIn('application/json', response.content_type)
    
    def test_html_response_content_type(self):
        """Test that HTML endpoints return correct content type."""
        response = self.client.get('/')
        self.assertIn('text/html', response.content_type)
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = self.client.get('/api/health')
        # CORS headers should be added by flask-cors
        self.assertEqual(response.status_code, 200)


class TestAPIErrorHandling(unittest.TestCase):
    """Test API error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_invalid_json_payload(self):
        """Test handling of invalid JSON."""
        response = self.client.post('/api/statistics/sample-size',
            data='not valid json',
            content_type='application/json'
        )
        
        # Should return error status
        self.assertIn(response.status_code, [400, 500])
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        response = self.client.post('/api/statistics/sample-size',
            json={'baseline_rate': 0.05},  # Missing other fields
            content_type='application/json'
        )
        
        # Should return error
        self.assertIn(response.status_code, [400, 500])
    
    def test_invalid_status_filter(self):
        """Test handling of invalid status filter."""
        response = self.client.get('/api/experiments?status=invalid_status')
        
        # Should return error
        self.assertIn(response.status_code, [400, 500])


class TestStatisticsEndpoints(unittest.TestCase):
    """Test statistics calculation endpoints."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_sample_size_different_parameters(self):
        """Test sample size with different parameters."""
        # Small effect size
        response1 = self.client.post('/api/statistics/sample-size',
            json={'baseline_rate': 0.05, 'expected_lift': 0.05, 'power': 0.80},
            content_type='application/json'
        )
        
        # Large effect size
        response2 = self.client.post('/api/statistics/sample-size',
            json={'baseline_rate': 0.05, 'expected_lift': 0.50, 'power': 0.80},
            content_type='application/json'
        )
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        # Smaller effect requires more samples
        self.assertGreater(
            data1['sample_size_per_variant'],
            data2['sample_size_per_variant']
        )
    
    def test_significance_with_different_data(self):
        """Test significance calculation with different datasets."""
        # Significant difference
        response1 = self.client.post('/api/statistics/significance',
            json={
                'control': {'successes': 100, 'total': 1000},
                'treatment': {'successes': 200, 'total': 1000},
                'metric_type': 'rate'
            },
            content_type='application/json'
        )
        
        # No difference
        response2 = self.client.post('/api/statistics/significance',
            json={
                'control': {'successes': 100, 'total': 1000},
                'treatment': {'successes': 101, 'total': 1000},
                'metric_type': 'rate'
            },
            content_type='application/json'
        )
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        self.assertTrue(data1['is_significant'])
        self.assertFalse(data2['is_significant'])


if __name__ == '__main__':
    unittest.main()





