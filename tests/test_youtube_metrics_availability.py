"""
Test YouTube Analytics API metric availability.

This test checks which metrics are actually available for your YouTube channel.
Some metrics require minimum subscriber counts or channel features to be enabled.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from youtube_analytics import YouTubeAnalytics


class TestYouTubeMetricsAvailability(unittest.TestCase):
    """Test which YouTube Analytics metrics are available for this channel."""
    
    @classmethod
    def setUpClass(cls):
        """Set up YouTube API connection once for all tests."""
        try:
            cls.youtube = YouTubeAnalytics()
            cls.api_available = True
            
            # Use recent dates with actual data
            cls.end_date = datetime.now().date()
            cls.start_date = cls.end_date - timedelta(days=30)  # Last 30 days
            
            print("\n" + "="*70)
            print("YouTube Analytics API Metric Availability Test")
            print("="*70)
            print(f"Testing period: {cls.start_date} to {cls.end_date}")
            print(f"Testing against your authenticated YouTube channel")
            print("="*70 + "\n")
            
        except Exception as e:
            cls.api_available = False
            cls.setup_error = str(e)
    
    def _test_metric(self, metric_name, description=""):
        """Helper method to test a single metric."""
        if not self.api_available:
            self.skipTest(f"YouTube API not available: {self.setup_error}")
        
        try:
            result = self.youtube.get_aggregate_metrics(
                start_date=str(self.start_date),
                end_date=str(self.end_date),
                metrics=[metric_name]
            )
            
            # Check if we got data back
            has_data = result.get('data') and len(result['data']) > 0
            value = result['data'][0].get(metric_name, 0) if has_data else 0
            
            print(f"✅ {metric_name:35} - Available (value: {value})")
            return True, value
            
        except Exception as e:
            error_msg = str(e)
            if "Unknown identifier" in error_msg:
                print(f"❌ {metric_name:35} - NOT available for your channel")
                return False, f"Not available: {error_msg[:50]}"
            elif "insufficient" in error_msg.lower():
                print(f"⚠️  {metric_name:35} - Insufficient permissions")
                return False, f"Permission issue: {error_msg[:50]}"
            else:
                print(f"⚠️  {metric_name:35} - Error: {error_msg[:50]}")
                return False, error_msg[:100]
    
    # Core Metrics (should work for all channels)
    
    def test_metric_views(self):
        """Test 'views' metric - View count (should always work)."""
        available, result = self._test_metric('views', 'Total view count')
        self.assertTrue(available, f"views metric should be available: {result}")
    
    def test_metric_likes(self):
        """Test 'likes' metric - Like count (should always work)."""
        available, result = self._test_metric('likes', 'Total likes')
        # Don't fail if likes not available (some channels disable)
        if not available:
            self.skipTest(f"Likes not available: {result}")
    
    def test_metric_comments(self):
        """Test 'comments' metric - Comment count."""
        available, result = self._test_metric('comments', 'Total comments')
        if not available:
            self.skipTest(f"Comments not available: {result}")
    
    def test_metric_shares(self):
        """Test 'shares' metric - Share count."""
        available, result = self._test_metric('shares', 'Total shares')
        if not available:
            self.skipTest(f"Shares not available: {result}")
    
    # Watch Time Metrics
    
    def test_metric_estimated_minutes_watched(self):
        """Test 'estimatedMinutesWatched' metric - Total watch time."""
        available, result = self._test_metric('estimatedMinutesWatched', 'Watch time in minutes')
        if not available:
            self.skipTest(f"EstimatedMinutesWatched not available: {result}")
    
    def test_metric_average_view_duration(self):
        """Test 'averageViewDuration' metric - Average view duration in seconds."""
        available, result = self._test_metric('averageViewDuration', 'Avg view duration')
        if not available:
            self.skipTest(f"AverageViewDuration not available: {result}")
    
    def test_metric_average_view_percentage(self):
        """Test 'averageViewPercentage' metric - Average percentage of video watched."""
        available, result = self._test_metric('averageViewPercentage', 'Avg % watched')
        if not available:
            self.skipTest(f"AverageViewPercentage not available: {result}")
    
    # Subscriber Metrics
    
    def test_metric_subscribers_gained(self):
        """Test 'subscribersGained' metric - New subscribers."""
        available, result = self._test_metric('subscribersGained', 'Subscribers gained')
        if not available:
            self.skipTest(f"SubscribersGained not available: {result}")
    
    def test_metric_subscribers_lost(self):
        """Test 'subscribersLost' metric - Lost subscribers."""
        available, result = self._test_metric('subscribersLost', 'Subscribers lost')
        if not available:
            self.skipTest(f"SubscribersLost not available: {result}")
    
    # Impression Metrics (require threshold)
    
    def test_metric_impressions(self):
        """Test 'impressions' metric - Impression count (requires ~1000 subs)."""
        available, result = self._test_metric('impressions', 'Total impressions')
        if not available:
            self.skipTest(f"Impressions not available - requires subscriber threshold: {result}")
    
    def test_metric_impression_click_through_rate(self):
        """Test 'impressionClickThroughRate' metric - CTR (requires ~1000 subs)."""
        available, result = self._test_metric('impressionClickThroughRate', 'Impression CTR')
        if not available:
            self.skipTest(f"ImpressionClickThroughRate not available - requires subscriber threshold: {result}")
    
    # Playlist Metrics
    
    def test_metric_videos_added_to_playlists(self):
        """Test 'videosAddedToPlaylists' metric."""
        available, result = self._test_metric('videosAddedToPlaylists', 'Videos added to playlists')
        if not available:
            self.skipTest(f"VideosAddedToPlaylists not available: {result}")
    
    def test_metric_videos_removed_from_playlists(self):
        """Test 'videosRemovedFromPlaylists' metric."""
        available, result = self._test_metric('videosRemovedFromPlaylists', 'Videos removed from playlists')
        if not available:
            self.skipTest(f"VideosRemovedFromPlaylists not available: {result}")
    
    # Card Metrics (requires cards feature)
    
    def test_metric_card_clicks(self):
        """Test 'cardClicks' metric - Card click count."""
        available, result = self._test_metric('cardClicks', 'Card clicks')
        if not available:
            self.skipTest(f"CardClicks not available - requires cards: {result}")
    
    def test_metric_card_teaser_clicks(self):
        """Test 'cardTeaserClicks' metric."""
        available, result = self._test_metric('cardTeaserClicks', 'Card teaser clicks')
        if not available:
            self.skipTest(f"CardTeaserClicks not available: {result}")
    
    def test_metric_card_impressions(self):
        """Test 'cardImpressions' metric."""
        available, result = self._test_metric('cardImpressions', 'Card impressions')
        if not available:
            self.skipTest(f"CardImpressions not available: {result}")
    
    def test_metric_card_teaser_impressions(self):
        """Test 'cardTeaserImpressions' metric."""
        available, result = self._test_metric('cardTeaserImpressions', 'Card teaser impressions')
        if not available:
            self.skipTest(f"CardTeaserImpressions not available: {result}")
    
    # Annotation Metrics (deprecated but still in API)
    
    def test_metric_annotation_click_through_rate(self):
        """Test 'annotationClickThroughRate' metric (deprecated feature)."""
        available, result = self._test_metric('annotationClickThroughRate', 'Annotation CTR')
        if not available:
            self.skipTest(f"AnnotationClickThroughRate not available - deprecated: {result}")
    
    def test_metric_annotation_close_rate(self):
        """Test 'annotationCloseRate' metric (deprecated feature)."""
        available, result = self._test_metric('annotationCloseRate', 'Annotation close rate')
        if not available:
            self.skipTest(f"AnnotationCloseRate not available - deprecated: {result}")
    
    # Dislike metric (hidden by YouTube but API might still have it)
    
    def test_metric_dislikes(self):
        """Test 'dislikes' metric (hidden by YouTube in 2021)."""
        available, result = self._test_metric('dislikes', 'Dislikes')
        if not available:
            self.skipTest(f"Dislikes not available - removed by YouTube: {result}")
    
    @classmethod
    def tearDownClass(cls):
        """Print summary after all tests."""
        print("\n" + "="*70)
        print("Test Complete!")
        print("="*70)
        print("\nCheck the results above to see which metrics work for your channel.")
        print("\nMetrics marked with ✅ can be used in your experiments.")
        print("Metrics marked with ❌ are not available for your channel.")
        print("Metrics marked with ⚠️  had errors - check the message.")
        print("\n" + "="*70 + "\n")


def run_metric_availability_test():
    """Run just the metric availability tests."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestYouTubeMetricsAvailability)
    runner = unittest.TextTestRunner(verbosity=2)
    return runner.run(suite)


if __name__ == '__main__':
    run_metric_availability_test()

