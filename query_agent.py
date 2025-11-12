"""Natural language query agent for YouTube Analytics data."""

import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

from youtube_analytics import YouTubeAnalytics

# Load environment variables
load_dotenv()


class QueryAgent:
    """Process natural language queries about YouTube Analytics data."""
    
    def __init__(self, youtube_api: YouTubeAnalytics):
        """
        Initialize the query agent.
        
        Args:
            youtube_api: YouTubeAnalytics instance for data fetching
        """
        self.youtube_api = youtube_api
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def process_query(self, question: str) -> Dict[str, Any]:
        """
        Process a natural language query and return results.
        
        Args:
            question: Natural language question about YouTube data
        
        Returns:
            Dictionary with query results, formatted data, and explanation
        """
        try:
            # Use OpenAI function calling to parse the query
            parsed_query = self._parse_query_with_llm(question)
            
            if 'error' in parsed_query:
                return {
                    'success': False,
                    'error': parsed_query['error'],
                    'explanation': parsed_query.get('explanation', 'Could not parse query')
                }
            
            # Execute the query based on parsed intent
            raw_data = self._execute_query(parsed_query)
            
            if 'error' in raw_data:
                return {
                    'success': False,
                    'error': raw_data['error'],
                    'explanation': raw_data.get('explanation', 'Failed to fetch data')
                }
            
            # Format the results for display
            formatted_result = self._format_results(question, parsed_query, raw_data)
            
            return {
                'success': True,
                'data': raw_data,
                'formatted': formatted_result,
                'query_info': parsed_query
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'explanation': 'An unexpected error occurred while processing your query.'
            }
    
    def _parse_query_with_llm(self, question: str) -> Dict[str, Any]:
        """
        Use OpenAI function calling to parse the natural language query.
        
        Args:
            question: Natural language question
        
        Returns:
            Parsed query parameters
        """
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_video_performance",
                    "description": "Get performance metrics for videos in a date range. Use this when user asks about specific videos, top performing videos, or video comparisons.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of metrics to retrieve (e.g., views, likes, comments, subscribersGained, averageViewDuration)"
                            },
                            "sort_by": {
                                "type": "string",
                                "description": "Metric to sort by (default: views)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Number of videos to return (default: 10)"
                            }
                        },
                        "required": ["start_date", "end_date", "metrics"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_aggregate_stats",
                    "description": "Get aggregate channel statistics for a date range. Use this when user asks about total/overall channel performance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_date": {
                                "type": "string",
                                "description": "Start date in YYYY-MM-DD format"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in YYYY-MM-DD format"
                            },
                            "metrics": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "List of metrics to retrieve (e.g., views, likes, comments, subscribersGained, estimatedMinutesWatched)"
                            }
                        },
                        "required": ["start_date", "end_date", "metrics"]
                    }
                }
            }
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are a YouTube Analytics query parser. Convert natural language questions into structured API calls.

Current date: {datetime.now().strftime('%Y-%m-%d')}

Date parsing rules:
- "last 3 months" = 90 days ago to today
- "last month" = 30 days ago to today
- "last week" = 7 days ago to today
- "this year" = January 1st of current year to today
- "last year" = January 1st to December 31st of previous year

Available metrics:
- views, likes, comments, shares
- subscribersGained, subscribersLost
- estimatedMinutesWatched, averageViewDuration, averageViewPercentage
- impressions, impressionClickThroughRate

Choose the appropriate function and extract the correct parameters."""
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                tools=tools,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                return {
                    'function': function_name,
                    'parameters': function_args,
                    'original_question': question
                }
            else:
                # LLM didn't call a function - it might not understand the query
                return {
                    'error': 'query_not_understood',
                    'explanation': message.content or "I couldn't understand how to query that data. Try asking about video performance or channel statistics with a specific time period."
                }
                
        except Exception as e:
            return {
                'error': 'parsing_failed',
                'explanation': f"Failed to parse query: {str(e)}"
            }
    
    def _execute_query(self, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the parsed query against YouTube Analytics API.
        
        Args:
            parsed_query: Parsed query parameters
        
        Returns:
            Raw data from YouTube API
        """
        function_name = parsed_query.get('function')
        params = parsed_query.get('parameters', {})
        
        try:
            if function_name == 'get_video_performance':
                return self._get_video_performance(params)
            elif function_name == 'get_aggregate_stats':
                return self._get_aggregate_stats(params)
            else:
                return {
                    'error': 'unknown_function',
                    'explanation': f"Unknown function: {function_name}"
                }
        except Exception as e:
            return {
                'error': 'api_error',
                'explanation': f"YouTube API error: {str(e)}"
            }
    
    def _get_video_performance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get video performance metrics."""
        start_date = params['start_date']
        end_date = params['end_date']
        metrics = params['metrics']
        sort_by = params.get('sort_by', 'views')
        limit = params.get('limit', 10)
        
        # Get all videos in date range
        videos = self.youtube_api.get_channel_videos_by_date_range(
            start_date=start_date,
            end_date=end_date,
            max_results=500
        )
        
        if not videos:
            return {
                'error': 'no_videos_found',
                'explanation': f"No videos found between {start_date} and {end_date}"
            }
        
        # Get metrics for these videos
        video_ids = [v['video_id'] for v in videos]
        
        metrics_data = self.youtube_api.get_video_metrics(
            video_ids=video_ids,
            start_date=start_date,
            end_date=end_date,
            metrics=metrics
        )
        
        # Combine video info with metrics
        video_info_map = {v['video_id']: v for v in videos}
        
        results = []
        for item in metrics_data.get('data', []):
            video_id = item.get('video')
            video_info = video_info_map.get(video_id, {})
            
            result = {
                'video_id': video_id,
                'title': video_info.get('title', 'Unknown'),
                'published_at': video_info.get('published_at', 'Unknown'),
                **item
            }
            results.append(result)
        
        # Sort and limit
        if sort_by in metrics and results:
            results.sort(key=lambda x: x.get(sort_by, 0), reverse=True)
        
        return {
            'type': 'video_performance',
            'videos': results[:limit],
            'total_videos': len(results),
            'date_range': {'start': start_date, 'end': end_date},
            'metrics': metrics
        }
    
    def _get_aggregate_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get aggregate channel statistics."""
        start_date = params['start_date']
        end_date = params['end_date']
        metrics = params['metrics']
        
        data = self.youtube_api.get_aggregate_metrics(
            start_date=start_date,
            end_date=end_date,
            metrics=metrics
        )
        
        # Extract the aggregated values
        stats = {}
        if data.get('data'):
            stats = data['data'][0] if len(data['data']) > 0 else {}
        
        return {
            'type': 'aggregate_stats',
            'statistics': stats,
            'date_range': {'start': start_date, 'end': end_date},
            'metrics': metrics
        }
    
    def _format_results(self, question: str, parsed_query: Dict, raw_data: Dict) -> str:
        """
        Format raw data into human-readable response using LLM.
        
        Args:
            question: Original question
            parsed_query: Parsed query info
            raw_data: Raw API data
        
        Returns:
            Formatted text response
        """
        try:
            # Prepare data summary for LLM
            data_summary = json.dumps(raw_data, indent=2, default=str)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a YouTube Analytics assistant. Format the query results into a clear, concise answer.

Guidelines:
- Answer the user's specific question directly
- Present data in a clear, organized way
- Use tables or lists for multiple items
- Include relevant metrics and numbers
- Be conversational but precise
- If showing video titles, make them prominent
- Format numbers with commas for readability (e.g., 1,234 views)"""
                    },
                    {
                        "role": "user",
                        "content": f"""Question: {question}

Data retrieved:
{data_summary}

Please format this into a clear answer to the user's question."""
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # Fallback to basic formatting
            return self._basic_format(raw_data)
    
    def _basic_format(self, raw_data: Dict) -> str:
        """Basic fallback formatting if LLM formatting fails."""
        if raw_data.get('type') == 'video_performance':
            videos = raw_data.get('videos', [])
            if not videos:
                return "No videos found for the specified criteria."
            
            result = f"Found {len(videos)} video(s):\n\n"
            for i, video in enumerate(videos, 1):
                result += f"{i}. {video.get('title', 'Unknown')}\n"
                for key, value in video.items():
                    if key not in ['video_id', 'title', 'video', 'published_at']:
                        result += f"   {key}: {value:,}\n" if isinstance(value, (int, float)) else f"   {key}: {value}\n"
                result += "\n"
            return result
            
        elif raw_data.get('type') == 'aggregate_stats':
            stats = raw_data.get('statistics', {})
            if not stats:
                return "No statistics found for the specified period."
            
            result = "Channel Statistics:\n\n"
            for key, value in stats.items():
                formatted_value = f"{value:,}" if isinstance(value, (int, float)) else value
                result += f"{key}: {formatted_value}\n"
            return result
        
        return "Data retrieved successfully, but formatting is unavailable."

