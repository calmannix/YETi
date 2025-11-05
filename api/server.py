"""Flask API server for YETi - YouTube Experiment Testing intelligence."""

import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request, send_file, render_template
from flask_cors import CORS
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from experiment_manager import ExperimentManager, Experiment, ExperimentStatus
from youtube_analytics import YouTubeAnalytics
from experiment_analyser import ExperimentAnalyser
from report_generator import ReportGenerator
from export_manager import ExportManager
from statistics_engine import StatisticsEngine
from models.variant import VideoVariant, VariantType, VariantManager
from models.experiment_enhanced import EnhancedExperiment
from insights_agent import InsightsAgent

# Setup Flask with template directory
template_dir = Path(__file__).parent / 'templates'
app = Flask(__name__, template_folder=str(template_dir))
CORS(app)  # Enable CORS for frontend

# Initialize managers
experiment_manager = ExperimentManager()
variant_manager = VariantManager()
export_manager = ExportManager()
report_generator = ReportGenerator()

# Lazy load YouTube API (only when needed)
youtube_api = None
experiment_analyser = None


def get_youtube_api():
    """Get or create YouTube API instance."""
    global youtube_api, experiment_analyser
    if youtube_api is None:
        youtube_api = YouTubeAnalytics()
        experiment_analyser = ExperimentAnalyser(youtube_api, experiment_manager)
    return youtube_api, experiment_analyser


@app.route('/')
def index():
    """Serve the dashboard."""
    return render_template('index.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.1.0'
    })


@app.route('/api/experiments', methods=['GET'])
def list_experiments():
    """List all experiments."""
    try:
        status_filter = request.args.get('status')
        status = ExperimentStatus(status_filter) if status_filter else None
        
        experiments = experiment_manager.list_experiments(status)
        
        return jsonify({
            'experiments': [exp.to_dict() for exp in experiments],
            'count': len(experiments)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<experiment_id>', methods=['GET'])
def get_experiment(experiment_id):
    """Get experiment details."""
    try:
        exp = experiment_manager.get_experiment(experiment_id)
        
        if not exp:
            return jsonify({'error': 'Experiment not found'}), 404
        
        # Convert to enhanced experiment if needed
        if not isinstance(exp, EnhancedExperiment):
            exp = EnhancedExperiment.from_experiment(exp)
        
        return jsonify(exp.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments', methods=['POST'])
def create_experiment():
    """Create a new experiment."""
    try:
        data = request.json
        
        # Create experiment from provided data
        from experiment_manager import SuccessCriteria, ComparisonOperator
        
        success_criteria = SuccessCriteria(
            metric=data['success_criteria']['metric'],
            threshold=data['success_criteria']['threshold'],
            operator=ComparisonOperator(data['success_criteria']['operator'])
        )
        
        experiment = Experiment(
            id=data['id'],
            name=data['name'],
            hypothesis=data['hypothesis'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            baseline_start=data.get('baseline_start'),
            baseline_end=data.get('baseline_end'),
            metrics=data['metrics'],
            success_criteria=success_criteria,
            video_ids=data.get('video_ids'),
            notes=data.get('notes', '')
        )
        
        exp_id = experiment_manager.create_experiment(experiment)
        
        return jsonify({
            'id': exp_id,
            'message': 'Experiment created successfully'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/experiments/<experiment_id>', methods=['PUT'])
def update_experiment(experiment_id):
    """Update an experiment."""
    try:
        data = request.json
        experiment_manager.update_experiment(experiment_id, data)
        
        return jsonify({'message': 'Experiment updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/experiments/<experiment_id>', methods=['DELETE'])
def delete_experiment(experiment_id):
    """Delete an experiment."""
    try:
        experiment_manager.delete_experiment(experiment_id)
        return jsonify({'message': 'Experiment deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# Start/Stop endpoints removed - status is now automatic based on dates
# Experiments are:
# - DRAFT if start_date is in the future
# - ACTIVE if today is between start_date and end_date
# - COMPLETED if end_date is in the past


@app.route('/api/experiments/<experiment_id>/analyze', methods=['POST'])
def analyze_experiment(experiment_id):
    """Analyse experiment results."""
    try:
        exp = experiment_manager.get_experiment(experiment_id)
        
        if not exp:
            return jsonify({'error': 'Experiment not found'}), 404
        
        # Get YouTube API
        _, analyser = get_youtube_api()
        
        # Run analysis
        analysis = analyser.analyse_experiment(exp)
        
        # Save results
        experiment_manager.update_experiment(experiment_id, {'results': analysis})
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<experiment_id>/report', methods=['GET'])
def get_experiment_report(experiment_id):
    """Get experiment report in specified format."""
    try:
        exp = experiment_manager.get_experiment(experiment_id)
        
        if not exp:
            return jsonify({'error': 'Experiment not found'}), 404
        
        if not exp.results:
            return jsonify({'error': 'Experiment not analyzed yet'}), 400
        
        report_format = request.args.get('format', 'text')
        
        if report_format == 'json':
            report = report_generator.generate_json_report(exp.results)
            return jsonify({'report': report})
        elif report_format == 'summary':
            report = report_generator.generate_summary(exp.results)
            return jsonify({'report': report})
        else:
            report = report_generator.generate_text_report(exp.results)
            return jsonify({'report': report})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/<experiment_id>/export', methods=['POST'])
def export_experiment(experiment_id):
    """Export experiment results to file."""
    try:
        exp = experiment_manager.get_experiment(experiment_id)
        
        if not exp:
            return jsonify({'error': 'Experiment not found'}), 404
        
        if not exp.results:
            return jsonify({'error': 'Experiment not analyzed yet'}), 400
        
        export_format = request.json.get('format', 'csv')
        
        if export_format == 'pdf':
            filepath = export_manager.export_to_pdf(exp.results)
        elif export_format == 'csv':
            filepath = export_manager.export_to_csv(exp.results)
        else:
            return jsonify({'error': 'Invalid export format'}), 400
        
        # Return file
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/experiments/next-id', methods=['GET'])
def get_next_experiment_id():
    """Get the next sequential experiment ID."""
    try:
        all_experiments = experiment_manager.list_experiments()
        if not all_experiments:
            return jsonify({'next_id': '1'})
        
        # Extract numeric IDs and find max
        numeric_ids = []
        for exp in all_experiments:
            try:
                numeric_ids.append(int(exp.id))
            except ValueError:
                continue
        
        next_id = str(max(numeric_ids) + 1) if numeric_ids else '1'
        return jsonify({'next_id': next_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/summary', methods=['GET'])
def dashboard_summary():
    """Get dashboard summary data."""
    try:
        all_experiments = experiment_manager.list_experiments()
        
        # Calculate statistics
        active = len([e for e in all_experiments if e.status == ExperimentStatus.ACTIVE])
        completed = len([e for e in all_experiments if e.status == ExperimentStatus.COMPLETED])
        successful = len([e for e in all_experiments 
                         if e.status == ExperimentStatus.COMPLETED and 
                         e.results and e.results.get('success')])
        
        ready_for_analysis = len(experiment_manager.get_ready_for_analysis())
        
        # Recent experiments
        recent = all_experiments[:5]
        
        return jsonify({
            'total_experiments': len(all_experiments),
            'active': active,
            'completed': completed,
            'successful': successful,
            'success_rate': (successful / completed * 100) if completed > 0 else 0,
            'ready_for_analysis': ready_for_analysis,
            'recent_experiments': [
                {
                    'id': e.id,
                    'name': e.name,
                    'status': e.status.value,
                    'created_at': e.created_at
                }
                for e in recent
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/channel/stats', methods=['GET'])
def get_channel_stats():
    """Get YouTube channel statistics."""
    try:
        from googleapiclient.discovery import build
        
        # Get YouTube API
        youtube_analytics, _ = get_youtube_api()
        
        # Build YouTube Data API v3 client
        youtube_data = build('youtube', 'v3', credentials=youtube_analytics.service._http.credentials)
        
        # Get channel information
        channels_response = youtube_data.channels().list(
            part='snippet,statistics,contentDetails',
            mine=True
        ).execute()
        
        if not channels_response.get('items'):
            return jsonify({'error': 'No channel found'}), 404
        
        channel = channels_response['items'][0]
        stats = channel['statistics']
        snippet = channel['snippet']
        
        # Get recent analytics for engagement metrics
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=28)  # Last 28 days
        
        # Get engagement metrics (views, likes, comments, shares)
        # Note: impressions/CTR not available for this channel type (likely Shorts-focused)
        try:
            analytics_response = youtube_analytics.service.reports().query(
                ids='channel==MINE',
                startDate=start_date.strftime('%Y-%m-%d'),
                endDate=end_date.strftime('%Y-%m-%d'),
                metrics='views,likes,comments,shares'
            ).execute()
            
            views_28d = 0
            likes_28d = 0
            comments_28d = 0
            shares_28d = 0
            engagement_rate = 0
            
            if analytics_response.get('rows'):
                row = analytics_response['rows'][0]
                views_28d = row[0] if len(row) > 0 else 0
                likes_28d = row[1] if len(row) > 1 else 0
                comments_28d = row[2] if len(row) > 2 else 0
                shares_28d = row[3] if len(row) > 3 else 0
                
                # Calculate engagement rate: (likes + comments + shares) / views
                if views_28d > 0:
                    engagement_rate = ((likes_28d + comments_28d + shares_28d) / views_28d) * 100
        except Exception as e:
            print(f"⚠️ Engagement metrics error: {e}")
            views_28d = None
            engagement_rate = None
        
        # Count videos (get uploads playlist)
        uploads_playlist_id = channel['contentDetails']['relatedPlaylists']['uploads']
        
        # Get total video count
        videos_response = youtube_data.playlistItems().list(
            part='contentDetails',
            playlistId=uploads_playlist_id,
            maxResults=1
        ).execute()
        
        total_videos = int(stats.get('videoCount', 0))
        
        # Try to count Shorts (videos < 60 seconds)
        shorts_count = 0
        try:
            # Get recent videos
            recent_videos_response = youtube_data.playlistItems().list(
                part='contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=50
            ).execute()
            
            video_ids = [item['contentDetails']['videoId'] for item in recent_videos_response.get('items', [])]
            
            if video_ids:
                videos_detail = youtube_data.videos().list(
                    part='contentDetails',
                    id=','.join(video_ids)
                ).execute()
                
                for video in videos_detail.get('items', []):
                    duration = video['contentDetails']['duration']
                    # Parse ISO 8601 duration (e.g., PT1M30S)
                    import re
                    match = re.match(r'PT(?:(\d+)M)?(?:(\d+)S)?', duration)
                    if match:
                        minutes = int(match.group(1) or 0)
                        seconds = int(match.group(2) or 0)
                        total_seconds = minutes * 60 + seconds
                        if total_seconds <= 60:
                            shorts_count += 1
        except Exception as e:
            print(f"Error counting shorts: {e}")
            shorts_count = None
        
        return jsonify({
            'channel_name': snippet['title'],
            'channel_id': channel['id'],
            'subscribers': int(stats.get('subscriberCount', 0)),
            'total_views': int(stats.get('viewCount', 0)),
            'total_videos': total_videos,
            'shorts_count': shorts_count,
            'views_28d': views_28d,
            'engagement_rate_28d': engagement_rate,
            'has_engagement_data': engagement_rate is not None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/variants', methods=['POST'])
def create_variant():
    """Create a video variant for A/B testing."""
    try:
        data = request.json
        
        variant = variant_manager.create_variant(
            experiment_id=data['experiment_id'],
            variant_type=VariantType(data['variant_type']),
            name=data['name'],
            video_ids=data.get('video_ids', []),
            description=data.get('description', ''),
            data=data.get('data', {}),
            is_control=data.get('is_control', False)
        )
        
        return jsonify(variant.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/variants/<experiment_id>', methods=['GET'])
def get_variants(experiment_id):
    """Get all variants for an experiment."""
    try:
        variants = variant_manager.get_variants_for_experiment(experiment_id)
        return jsonify({
            'variants': [v.to_dict() for v in variants],
            'count': len(variants)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/insights/ai-analysis', methods=['GET'])
def get_ai_insights():
    """Get AI-generated insights from all experiments."""
    try:
        # Get all experiments with results
        all_experiments = experiment_manager.list_experiments()
        
        # Get channel info for context
        try:
            _, analyser = get_youtube_api()
            from googleapiclient.discovery import build
            youtube_data = build('youtube', 'v3', credentials=analyser.youtube.service._http.credentials)
            channels_response = youtube_data.channels().list(
                part='snippet,statistics',
                mine=True
            ).execute()
            
            if channels_response.get('items'):
                channel = channels_response['items'][0]
                channel_info = {
                    'channel_name': channel['snippet']['title'],
                    'niche': 'Japanese property investment',
                    'subscribers': int(channel['statistics'].get('subscriberCount', 0)),
                    'total_videos': int(channel['statistics'].get('videoCount', 0))
                }
            else:
                channel_info = None
        except:
            channel_info = None
        
        # Generate insights using AI
        insights_agent = InsightsAgent()
        insights = insights_agent.generate_insights(all_experiments, channel_info)
        
        return jsonify(insights)
        
    except ValueError as e:
        # API key not configured
        return jsonify({
            'error': 'AI insights not configured',
            'message': str(e),
            'setup_instructions': 'Add your OPENAI_API_KEY to the .env file'
        }), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/statistics/significance', methods=['POST'])
def calculate_significance():
    """Calculate statistical significance for provided data."""
    try:
        data = request.json
        
        stats_engine = StatisticsEngine(confidence_level=data.get('confidence_level', 0.95))
        
        result = stats_engine.analyze_experiment_results(
            control_data=data['control'],
            treatment_data=data['treatment'],
            metric_type=data.get('metric_type', 'rate')
        )
        
        return jsonify({
            'is_significant': result.is_significant,
            'p_value': result.p_value,
            'effect_size': result.effect_size,
            'power': result.power,
            'conclusion': result.conclusion
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/statistics/sample-size', methods=['POST'])
def calculate_sample_size():
    """Calculate required sample size for experiment."""
    try:
        data = request.json
        
        stats_engine = StatisticsEngine()
        
        sample_size = stats_engine.calculate_minimum_sample_size(
            baseline_rate=data['baseline_rate'],
            expected_lift=data['expected_lift'],
            power=data.get('power', 0.80)
        )
        
        return jsonify({
            'sample_size_per_variant': sample_size,
            'total_sample_size': sample_size * 2
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500


def main():
    """Run the Flask server."""
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print("=" * 70)
    print("YouTube Experiment Manager - Web API")
    print("=" * 70)
    print(f"Server running at: http://localhost:{port}")
    print(f"Dashboard: http://localhost:{port}/")
    print(f"API Docs: http://localhost:{port}/api/health")
    print("=" * 70)
    print("\nPress Ctrl+C to stop the server")
    print()
    
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    main()

