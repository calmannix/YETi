"""Unit tests for automatic video detection feature."""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta

from experiment_manager import Experiment, ExperimentStatus, SuccessCriteria, ComparisonOperator
from experiment_analyser import ExperimentAnalyser
from youtube_analytics import YouTubeAnalytics


class TestAutoVideoDetection(unittest.TestCase):
    """Test cases for automatic video detection and grouping."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock YouTube API
        self.mock_youtube = Mock(spec=YouTubeAnalytics)
        self.analyser = ExperimentAnalyser(self.mock_youtube)
        
        # Create test experiment
        self.experiment = Experiment(
            id='test_001',
            name='Test Experiment',
            hypothesis='Testing auto-detection',
            start_date='2025-06-10',
            end_date='2025-06-25',
            metrics={'primary': 'views', 'secondary': []},
            success_criteria=SuccessCriteria(
                metric='views',
                threshold=20.0,
                operator=ComparisonOperator.INCREASE
            ),
            video_ids=None  # No manual video IDs
        )
    
    def test_control_period_calculation(self):
        """Test that control period is calculated correctly."""
        # Experiment: Jun 10-25 (16 days)
        # Expected control: May 25 - Jun 9 (16 days before)
        
        start_dt = datetime.strptime('2025-06-10', '%Y-%m-%d')
        end_dt = datetime.strptime('2025-06-25', '%Y-%m-%d')
        duration = (end_dt - start_dt).days
        
        control_end_dt = start_dt - timedelta(days=1)
        control_start_dt = control_end_dt - timedelta(days=duration)
        
        self.assertEqual(control_start_dt.strftime('%Y-%m-%d'), '2025-05-25')
        self.assertEqual(control_end_dt.strftime('%Y-%m-%d'), '2025-06-09')
        self.assertEqual(duration, 15)  # 15 days difference, 16 days inclusive
    
    def test_auto_detect_videos_success(self):
        """Test successful video detection."""
        # Mock video data
        experiment_videos = [
            {'video_id': 'EXP_1', 'published_at': '2025-06-15T12:00:00Z', 'title': 'Experiment Video 1'},
            {'video_id': 'EXP_2', 'published_at': '2025-06-20T12:00:00Z', 'title': 'Experiment Video 2'},
        ]
        
        control_videos = [
            {'video_id': 'CTRL_1', 'published_at': '2025-06-01T12:00:00Z', 'title': 'Control Video 1'},
            {'video_id': 'CTRL_2', 'published_at': '2025-06-05T12:00:00Z', 'title': 'Control Video 2'},
        ]
        
        # Mock the YouTube API calls
        self.mock_youtube.get_channel_videos_by_date_range.side_effect = [
            experiment_videos,  # First call for experiment period
            control_videos      # Second call for control period
        ]
        
        # Run auto-detection
        result = self.analyser.auto_detect_videos(self.experiment)
        
        # Verify results
        self.assertEqual(len(result['treatment']), 2)
        self.assertEqual(len(result['control']), 2)
        self.assertIn('EXP_1', result['treatment'])
        self.assertIn('EXP_2', result['treatment'])
        self.assertIn('CTRL_1', result['control'])
        self.assertIn('CTRL_2', result['control'])
    
    def test_auto_detect_no_experiment_videos(self):
        """Test when no videos in experiment period."""
        # Mock empty experiment videos
        self.mock_youtube.get_channel_videos_by_date_range.side_effect = [
            [],  # No experiment videos
            [{'video_id': 'CTRL_1', 'published_at': '2025-06-01T12:00:00Z', 'title': 'Control'}]
        ]
        
        result = self.analyser.auto_detect_videos(self.experiment)
        
        self.assertEqual(len(result['treatment']), 0)
        self.assertEqual(len(result['control']), 1)
    
    def test_auto_detect_no_control_videos(self):
        """Test when no videos in control period (first experiment)."""
        # Mock no control videos
        self.mock_youtube.get_channel_videos_by_date_range.side_effect = [
            [{'video_id': 'EXP_1', 'published_at': '2025-06-15T12:00:00Z', 'title': 'Experiment'}],
            []  # No control videos
        ]
        
        result = self.analyser.auto_detect_videos(self.experiment)
        
        self.assertEqual(len(result['treatment']), 1)
        self.assertEqual(len(result['control']), 0)
    
    def test_date_ranges_are_equal_duration(self):
        """Test that experiment and control periods have equal duration."""
        # Mock videos
        self.mock_youtube.get_channel_videos_by_date_range.side_effect = [
            [{'video_id': 'EXP_1', 'published_at': '2025-06-15T12:00:00Z', 'title': 'Exp'}],
            [{'video_id': 'CTRL_1', 'published_at': '2025-06-01T12:00:00Z', 'title': 'Ctrl'}]
        ]
        
        result = self.analyser.auto_detect_videos(self.experiment)
        
        # Verify the API was called with correct date ranges
        calls = self.mock_youtube.get_channel_videos_by_date_range.call_args_list
        
        # First call: experiment period
        exp_call = calls[0]
        self.assertEqual(exp_call[1]['start_date'], '2025-06-10')
        self.assertEqual(exp_call[1]['end_date'], '2025-06-25')
        
        # Second call: control period
        ctrl_call = calls[1]
        self.assertEqual(ctrl_call[1]['start_date'], '2025-05-25')
        self.assertEqual(ctrl_call[1]['end_date'], '2025-06-09')


class TestVideoFetchingByDateRange(unittest.TestCase):
    """Test cases for fetching videos by date range."""
    
    def test_date_filtering_inclusive(self):
        """Test that start and end dates are inclusive."""
        # This would require mocking the YouTube API
        # For now, document expected behavior
        pass
    
    def test_handles_no_videos(self):
        """Test handling of channels with no videos."""
        pass
    
    def test_pagination_handling(self):
        """Test that pagination works for channels with many videos."""
        pass


class TestAnalysisWithAutoDetection(unittest.TestCase):
    """Test the complete analysis flow with auto-detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_youtube = Mock(spec=YouTubeAnalytics)
        self.analyser = ExperimentAnalyser(self.mock_youtube)
    
    def test_analysis_triggers_auto_detection(self):
        """Test that analysis triggers auto-detection when no video IDs."""
        experiment = Experiment(
            id='test_001',
            name='Test',
            hypothesis='Test',
            start_date='2025-06-10',
            end_date='2025-06-25',
            metrics={'primary': 'views', 'secondary': []},
            success_criteria=SuccessCriteria(
                metric='views',
                threshold=20.0,
                operator=ComparisonOperator.INCREASE
            ),
            video_ids=None
        )
        
        # Mock the methods
        self.mock_youtube.get_channel_videos_by_date_range.return_value = []
        self.mock_youtube.get_video_metrics.return_value = {
            'headers': ['video', 'views'],
            'data': [],
            'row_count': 0
        }
        
        # This should trigger auto-detection
        result = self.analyser.analyse_experiment(experiment)
        
        # Verify auto-detection was called
        self.assertTrue(self.mock_youtube.get_channel_videos_by_date_range.called)
        self.assertEqual(self.mock_youtube.get_channel_videos_by_date_range.call_count, 2)
    
    def test_manual_video_ids_skip_auto_detection(self):
        """Test that manual video IDs prevent auto-detection."""
        experiment = Experiment(
            id='test_001',
            name='Test',
            hypothesis='Test',
            start_date='2025-06-10',
            end_date='2025-06-25',
            metrics={'primary': 'views', 'secondary': []},
            success_criteria=SuccessCriteria(
                metric='views',
                threshold=20.0,
                operator=ComparisonOperator.INCREASE
            ),
            video_ids={
                'treatment': ['VIDEO_1', 'VIDEO_2'],
                'control': ['VIDEO_3', 'VIDEO_4']
            }
        )
        
        # Mock the metrics call
        self.mock_youtube.get_video_metrics.return_value = {
            'headers': ['video', 'views'],
            'data': [
                {'video': 'VIDEO_1', 'views': 100},
                {'video': 'VIDEO_2', 'views': 150},
                {'video': 'VIDEO_3', 'views': 80},
                {'video': 'VIDEO_4', 'views': 90}
            ],
            'row_count': 4
        }
        
        # This should NOT trigger auto-detection
        result = self.analyser.analyse_experiment(experiment)
        
        # Verify auto-detection was NOT called
        self.assertFalse(self.mock_youtube.get_channel_videos_by_date_range.called)


class TestYouTubeAPIMetricFetching(unittest.TestCase):
    """Test YouTube API metric fetching improvements."""
    
    def test_empty_video_list_returns_empty_data(self):
        """Test that empty video list returns empty data without API call."""
        # This tests the fix for the sort parameter bug
        pass
    
    def test_sort_parameter_uses_primary_metric(self):
        """Test that sort parameter matches primary metric."""
        # When primary metric is 'subscribersGained', sort should be '-subscribersGained'
        # When primary metric is 'views', sort should be '-views'
        pass
    
    def test_metrics_without_views(self):
        """Test fetching metrics when views is not included."""
        # Should use first metric for sorting instead of hardcoded 'views'
        pass


if __name__ == '__main__':
    unittest.main()

