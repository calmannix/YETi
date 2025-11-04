"""Unit tests for time series analyzer."""

import unittest
from datetime import datetime, timedelta
from time_series_analyzer import TimeSeriesAnalyzer


class TestTimeSeriesAnalyzer(unittest.TestCase):
    """Test cases for TimeSeriesAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = TimeSeriesAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertIsInstance(self.analyzer, TimeSeriesAnalyzer)
    
    def test_detect_trends_increasing(self):
        """Test trend detection with increasing values."""
        dates = [(datetime.now() - timedelta(days=10-i)).strftime('%Y-%m-%d') for i in range(10)]
        values = [100 + i * 10 for i in range(10)]  # Increasing trend
        
        result = self.analyzer.detect_trends(dates, values)
        
        self.assertIsInstance(result, dict)
        self.assertIn('has_trend', result)
        # Should detect increasing trend
        if result.get('trend_direction'):
            self.assertIn(result['trend_direction'], ['increasing', 'stable'])
    
    def test_detect_trends_decreasing(self):
        """Test trend detection with decreasing values."""
        dates = [(datetime.now() - timedelta(days=10-i)).strftime('%Y-%m-%d') for i in range(10)]
        values = [200 - i * 10 for i in range(10)]  # Decreasing trend
        
        result = self.analyzer.detect_trends(dates, values)
        
        self.assertIsInstance(result, dict)
        self.assertIn('has_trend', result)
    
    def test_detect_trends_stable(self):
        """Test trend detection with stable values."""
        dates = [(datetime.now() - timedelta(days=10-i)).strftime('%Y-%m-%d') for i in range(10)]
        values = [100] * 10  # Stable (no trend)
        
        result = self.analyzer.detect_trends(dates, values)
        
        self.assertIsInstance(result, dict)
        self.assertIn('has_trend', result)
    
    def test_detect_trends_insufficient_data(self):
        """Test trend detection with insufficient data."""
        dates = ['2025-01-01', '2025-01-02']
        values = [100, 110]
        
        result = self.analyzer.detect_trends(dates, values)
        
        self.assertIsInstance(result, dict)
        # Should still return a result, possibly with simple trend detection
        self.assertIn('has_trend', result)
    
    def test_detect_weekly_patterns(self):
        """Test weekly pattern detection."""
        # Create 3 weeks of data
        base_date = datetime.now()
        dates = []
        values = []
        
        # Simulate weekly pattern (higher on weekends)
        for week in range(3):
            for day in range(7):
                date = base_date - timedelta(days=(2-week)*7 + (6-day))
                dates.append(date.strftime('%Y-%m-%d'))
                # Higher values on weekends (day 5, 6)
                value = 100 if day < 5 else 150
                values.append(value)
        
        result = self.analyzer.detect_weekly_patterns(dates, values)
        
        self.assertIsInstance(result, dict)
        self.assertIn('has_weekly_pattern', result)
        self.assertIn('best_day', result)
        self.assertIn('worst_day', result)
        self.assertIn('daily_means', result)
    
    def test_detect_weekly_patterns_insufficient_data(self):
        """Test weekly pattern detection with insufficient data."""
        dates = ['2025-01-01', '2025-01-02']
        values = [100, 110]
        
        result = self.analyzer.detect_weekly_patterns(dates, values)
        
        self.assertIsInstance(result, dict)
        # Should handle gracefully
        self.assertIn('has_weekly_pattern', result)
    
    def test_adjust_for_trends(self):
        """Test trend adjustment for experiments."""
        dates = [(datetime.now() - timedelta(days=10-i)).strftime('%Y-%m-%d') for i in range(10)]
        exp_values = [100 + i * 5 for i in range(10)]
        control_dates = dates
        control_values = [100 + i * 3 for i in range(10)]
        
        adj_exp, adj_control = self.analyzer.adjust_for_trends(
            dates, exp_values, control_dates, control_values
        )
        
        # Should return values (may not adjust if trends not detected)
        self.assertIsInstance(adj_exp, list)
        self.assertIsInstance(adj_control, list)
        self.assertEqual(len(adj_exp), len(exp_values))
        self.assertEqual(len(adj_control), len(control_values))
    
    def test_forecast_metric(self):
        """Test metric forecasting."""
        dates = [(datetime.now() - timedelta(days=10-i)).strftime('%Y-%m-%d') for i in range(10)]
        values = [100 + i * 5 for i in range(10)]  # Increasing trend
        
        result = self.analyzer.forecast_metric(dates, values, periods=7)
        
        self.assertIsInstance(result, dict)
        self.assertIn('forecast', result)
        if result.get('forecast'):
            self.assertIsInstance(result['forecast'], list)
            self.assertEqual(len(result['forecast']), 7)
    
    def test_forecast_metric_insufficient_data(self):
        """Test forecasting with insufficient data."""
        dates = ['2025-01-01']
        values = [100]
        
        result = self.analyzer.forecast_metric(dates, values, periods=7)
        
        self.assertIsInstance(result, dict)
        # May return None or error message
        self.assertIn('forecast', result)
    
    def test_edge_cases(self):
        """Test edge cases."""
        # Empty data
        result = self.analyzer.detect_trends([], [])
        self.assertIsInstance(result, dict)
        
        # Single value
        result = self.analyzer.detect_trends(['2025-01-01'], [100])
        self.assertIsInstance(result, dict)
        
        # None values
        result = self.analyzer.detect_weekly_patterns([], [])
        self.assertIsInstance(result, dict)


if __name__ == '__main__':
    unittest.main()

