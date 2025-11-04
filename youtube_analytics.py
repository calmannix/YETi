"""YouTube Analytics API integration for experiment tracking."""

import os
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/yt-analytics.readonly',  # Analytics metrics
    'https://www.googleapis.com/auth/youtube.readonly'         # Channel info, video details
]


class YouTubeAnalytics:
    """Interface to YouTube Analytics API."""

    def __init__(self, credentials_file: str = 'credentials.json'):
        self.credentials_file = credentials_file
        self.token_file = 'token.pickle'
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with YouTube Analytics API."""
        creds = None

        # Load saved credentials
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('youtubeAnalytics', 'v2', credentials=creds)

    def get_video_metrics(
        self,
        video_ids: List[str],
        start_date: str,
        end_date: str,
        metrics: List[str]
    ) -> Dict:
        """
        Fetch metrics for specific videos in a date range.

        Args:
            video_ids: List of YouTube video IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metrics: List of metrics to fetch (views, likes, comments, etc.)

        Returns:
            Dictionary with video metrics
        """
        if not video_ids:
            # Return empty result if no videos
            return {'headers': [], 'data': [], 'row_count': 0}
        
        video_filter = f"video=={','.join(video_ids)}"
        metrics_str = ','.join(metrics)
        
        # Determine sort order - use first metric if views not available
        sort_metric = 'views' if 'views' in metrics else metrics[0]

        response = self.service.reports().query(
            ids='channel==MINE',
            startDate=start_date,
            endDate=end_date,
            metrics=metrics_str,
            dimensions='video',
            filters=video_filter,
            sort=f'-{sort_metric}'
        ).execute()

        return self._parse_response(response)

    def get_aggregate_metrics(
        self,
        start_date: str,
        end_date: str,
        metrics: List[str],
        dimensions: Optional[List[str]] = None
    ) -> Dict:
        """
        Fetch aggregate channel metrics.

        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            metrics: List of metrics to fetch
            dimensions: Optional dimensions to group by

        Returns:
            Dictionary with aggregated metrics
        """
        params = {
            'ids': 'channel==MINE',
            'startDate': start_date,
            'endDate': end_date,
            'metrics': ','.join(metrics)
        }

        if dimensions:
            params['dimensions'] = ','.join(dimensions)

        response = self.service.reports().query(**params).execute()
        return self._parse_response(response)

    def _parse_response(self, response: Dict) -> Dict:
        """Parse API response into usable format."""
        if 'rows' not in response:
            return {'headers': response.get('columnHeaders', []), 'data': []}

        headers = [col['name'] for col in response['columnHeaders']]
        rows = response['rows']

        # Convert to list of dictionaries
        data = []
        for row in rows:
            data.append(dict(zip(headers, row)))

        return {
            'headers': headers,
            'data': data,
            'row_count': len(data)
        }

    def get_channel_videos_by_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_results: int = 500
    ) -> List[Dict]:
        """
        Fetch all channel videos published in a date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format (inclusive). None = from beginning
            end_date: End date in YYYY-MM-DD format (inclusive). None = until now
            max_results: Maximum number of videos to fetch (default 500)
        
        Returns:
            List of dicts with 'video_id' and 'published_at' for each video
        """
        # Build YouTube Data API v3 client using same credentials
        youtube_data = build('youtube', 'v3', credentials=self.service._http.credentials)
        
        # Get channel's uploads playlist ID
        channels_response = youtube_data.channels().list(
            part='contentDetails',
            mine=True
        ).execute()
        
        if not channels_response.get('items'):
            return []
        
        uploads_playlist_id = channels_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Fetch all videos from uploads playlist
        videos = []
        next_page_token = None
        
        # Convert dates to datetime for comparison
        start_dt = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None
        # End date should be end of day
        if end_dt:
            end_dt = end_dt.replace(hour=23, minute=59, second=59)
        
        while True:
            request = youtube_data.playlistItems().list(
                part='contentDetails,snippet',
                playlistId=uploads_playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response.get('items', []):
                video_id = item['contentDetails']['videoId']
                published_at_str = item['snippet']['publishedAt']
                
                # Parse ISO 8601 datetime
                published_at = datetime.strptime(published_at_str, '%Y-%m-%dT%H:%M:%SZ')
                
                # Check if video is within date range
                include_video = True
                if start_dt and published_at < start_dt:
                    include_video = False
                if end_dt and published_at > end_dt:
                    include_video = False
                
                if include_video:
                    videos.append({
                        'video_id': video_id,
                        'published_at': published_at_str,
                        'title': item['snippet']['title']
                    })
            
            next_page_token = response.get('nextPageToken')
            
            # Stop if no more pages or reached max results
            if not next_page_token or len(videos) >= max_results:
                break
        
        return videos
    
    def get_available_metrics(self) -> List[str]:
        """Return list of common YouTube Analytics metrics."""
        return [
            'views',
            'estimatedMinutesWatched',
            'averageViewDuration',
            'averageViewPercentage',
            'subscribersGained',
            'subscribersLost',
            'likes',
            'dislikes',
            'comments',
            'shares',
            'videosAddedToPlaylists',
            'videosRemovedFromPlaylists',
            'cardClicks',
            'cardTeaserClicks',
            'cardImpressions',
            'cardTeaserImpressions',
            'annotationClickThroughRate',
            'annotationCloseRate',
            'impressions',
            'impressionClickThroughRate'
        ]
