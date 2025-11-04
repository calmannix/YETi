"""Analyse experiment results and determine success."""

import statistics
from typing import Dict, List, Optional
from datetime import datetime

from experiment_manager import Experiment, ComparisonOperator
from youtube_analytics import YouTubeAnalytics


class ExperimentAnalyser:
    """Analyse YouTube experiment results."""

    def __init__(self, youtube_api: YouTubeAnalytics, experiment_manager=None):
        self.youtube = youtube_api
        self.experiment_manager = experiment_manager

    def auto_detect_videos(self, experiment: Experiment) -> Dict[str, List[str]]:
        """
        Automatically detect and group videos based on experiment dates.
        
        Experiment group: Videos published between start_date and end_date
        Control group: Videos from the last SUCCESSFUL experiment
                      If no successful experiment exists, uses previous period (same duration)
        
        Returns:
            Dictionary with 'treatment' and 'control' video ID lists
        """
        from datetime import datetime, timedelta
        
        print(f"\nAuto-detecting videos for experiment: {experiment.id}")
        print(f"Experiment period: {experiment.start_date} to {experiment.end_date}")
        
        # Try to find last successful experiment to use as control
        control_start = None
        control_end = None
        control_source = "previous period"
        
        if self.experiment_manager:
            last_success = self.experiment_manager.get_last_successful_experiment(
                before_date=experiment.start_date
            )
            
            if last_success:
                # Use the last successful experiment's period as control
                control_start = last_success.start_date
                control_end = last_success.end_date
                control_source = f"last successful experiment (ID: {last_success.id})"
                print(f"📊 Found last successful experiment: {last_success.id}")
                print(f"   Using its period as control baseline: {control_start} to {control_end}")
        
        # Fallback: If no successful experiment, use previous period of same duration
        if not control_start:
            start_dt = datetime.strptime(experiment.start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(experiment.end_date, '%Y-%m-%d')
            duration = (end_dt - start_dt).days
            
            control_end_dt = start_dt - timedelta(days=1)
            control_start_dt = control_end_dt - timedelta(days=duration)
            
            control_start = control_start_dt.strftime('%Y-%m-%d')
            control_end = control_end_dt.strftime('%Y-%m-%d')
            control_source = "previous period (no successful experiments yet)"
            print(f"ℹ️  No successful experiments found - using {control_source}")
        
        print(f"Control period: {control_start} to {control_end} (from {control_source})")
        
        # Get experiment videos (published during experiment period)
        experiment_videos = self.youtube.get_channel_videos_by_date_range(
            start_date=experiment.start_date,
            end_date=experiment.end_date
        )
        
        # Get control videos (published during previous experiment period)
        control_videos = self.youtube.get_channel_videos_by_date_range(
            start_date=control_start,
            end_date=control_end
        )
        
        experiment_ids = [v['video_id'] for v in experiment_videos]
        control_ids = [v['video_id'] for v in control_videos]
        
        print(f"✓ Found {len(experiment_ids)} videos in experiment period")
        print(f"✓ Found {len(control_ids)} videos in control period ({control_source})")
        
        if len(experiment_ids) == 0:
            print(f"⚠️  Warning: No videos found in experiment period!")
            print(f"   Make sure videos are published between {experiment.start_date} and {experiment.end_date}")
        
        if len(control_ids) == 0:
            print(f"⚠️  Warning: No control videos found!")
            print(f"   No videos were published during the control period {control_start} to {control_end}")
            print(f"   Consider adjusting your experiment dates or this might be your first experiment")
        
        # Log some sample videos for verification
        if experiment_ids:
            print(f"\nSample experiment videos:")
            for video in experiment_videos[:3]:
                print(f"  - {video['title'][:60]}... (Published: {video['published_at'][:10]})")
            if len(experiment_videos) > 3:
                print(f"  ... and {len(experiment_videos) - 3} more")
        
        if control_ids:
            print(f"\nSample control videos:")
            for video in control_videos[:3]:
                print(f"  - {video['title'][:60]}... (Published: {video['published_at'][:10]})")
            if len(control_videos) > 3:
                print(f"  ... and {len(control_videos) - 3} more")
        
        return {
            'treatment': experiment_ids,
            'control': control_ids
        }

    def analyse_experiment(self, experiment: Experiment) -> Dict:
        """
        Run complete analysis on an experiment.

        Returns:
            Dictionary with analysis results, conclusions, and success status
        """
        # Auto-detect videos if not manually specified
        if not experiment.video_ids or (
            isinstance(experiment.video_ids, dict) and 
            not experiment.video_ids.get('treatment') and 
            not experiment.video_ids.get('control')
        ):
            print("\n" + "="*70)
            print("AUTO-DETECTING VIDEOS BASED ON PUBLISH DATES")
            print("="*70)
            video_groups = self.auto_detect_videos(experiment)
            # Temporarily assign for this analysis
            experiment.video_ids = video_groups
            print("\n" + "="*70)
            print("PROCEEDING WITH ANALYSIS")
            print("="*70)
        
        # Collect data
        experiment_data = self._collect_experiment_data(experiment)
        baseline_data = self._collect_baseline_data(experiment)

        # Analyse metrics
        analysis = {
            'experiment_id': experiment.id,
            'experiment_name': experiment.name,
            'hypothesis': experiment.hypothesis,
            'analysis_date': datetime.now().isoformat(),
            'period': {
                'baseline': f"{experiment.baseline_start} to {experiment.baseline_end}" if experiment.baseline_start else None,
                'experiment': f"{experiment.start_date} to {experiment.end_date}"
            },
            'metrics': {},
            'success': False,
            'conclusion': ''
        }

        # Compare metrics
        primary_metric = experiment.metrics['primary']
        secondary_metrics = experiment.metrics.get('secondary', [])

        # Analyse primary metric
        primary_result = self._compare_metric(
            metric_name=primary_metric,
            experiment_data=experiment_data,
            baseline_data=baseline_data,
            experiment=experiment
        )
        analysis['metrics'][primary_metric] = primary_result

        # Check success criteria
        analysis['success'] = self._check_success_criteria(
            primary_result,
            experiment.success_criteria
        )

        # Analyse secondary metrics
        for metric in secondary_metrics:
            result = self._compare_metric(
                metric_name=metric,
                experiment_data=experiment_data,
                baseline_data=baseline_data,
                experiment=experiment
            )
            analysis['metrics'][metric] = result

        # Generate conclusion
        analysis['conclusion'] = self._generate_conclusion(analysis, experiment)

        return analysis

    def _collect_experiment_data(self, experiment: Experiment) -> Dict:
        """Collect metrics during experiment period."""
        metrics = [experiment.metrics['primary']] + experiment.metrics.get('secondary', [])

        if experiment.video_ids:
            # Collect for specific videos
            all_videos = []
            if 'treatment' in experiment.video_ids:
                all_videos.extend(experiment.video_ids['treatment'])
            if 'control' in experiment.video_ids:
                all_videos.extend(experiment.video_ids['control'])

            data = self.youtube.get_video_metrics(
                video_ids=all_videos,
                start_date=experiment.start_date,
                end_date=experiment.end_date,
                metrics=metrics
            )
        else:
            # Aggregate channel metrics
            data = self.youtube.get_aggregate_metrics(
                start_date=experiment.start_date,
                end_date=experiment.end_date,
                metrics=metrics
            )

        return data

    def _collect_baseline_data(self, experiment: Experiment) -> Optional[Dict]:
        """Collect baseline metrics before experiment."""
        if not experiment.baseline_start or not experiment.baseline_end:
            return None

        metrics = [experiment.metrics['primary']] + experiment.metrics.get('secondary', [])

        if experiment.video_ids:
            all_videos = []
            if 'treatment' in experiment.video_ids:
                all_videos.extend(experiment.video_ids['treatment'])
            if 'control' in experiment.video_ids:
                all_videos.extend(experiment.video_ids['control'])

            data = self.youtube.get_video_metrics(
                video_ids=all_videos,
                start_date=experiment.baseline_start,
                end_date=experiment.baseline_end,
                metrics=metrics
            )
        else:
            data = self.youtube.get_aggregate_metrics(
                start_date=experiment.baseline_start,
                end_date=experiment.baseline_end,
                metrics=metrics
            )

        return data

    def _compare_metric(
        self,
        metric_name: str,
        experiment_data: Dict,
        baseline_data: Optional[Dict],
        experiment: Experiment
    ) -> Dict:
        """Compare metric between baseline and experiment periods."""
        # Calculate experiment metric value
        exp_value = self._extract_metric_value(experiment_data, metric_name)

        result = {
            'metric': metric_name,
            'experiment_value': exp_value,
            'baseline_value': None,
            'change': None,
            'change_percent': None
        }

        if baseline_data:
            baseline_value = self._extract_metric_value(baseline_data, metric_name)
            result['baseline_value'] = baseline_value

            if baseline_value and baseline_value != 0:
                change = exp_value - baseline_value
                change_percent = (change / baseline_value) * 100

                result['change'] = change
                result['change_percent'] = round(change_percent, 2)

        # If comparing treatment vs control
        if experiment.video_ids and 'treatment' in experiment.video_ids and 'control' in experiment.video_ids:
            treatment_value = self._extract_metric_for_videos(
                experiment_data,
                metric_name,
                experiment.video_ids['treatment']
            )
            control_value = self._extract_metric_for_videos(
                experiment_data,
                metric_name,
                experiment.video_ids['control']
            )

            result['treatment_value'] = treatment_value
            result['control_value'] = control_value

            if control_value and control_value != 0:
                change = treatment_value - control_value
                change_percent = (change / control_value) * 100
                result['treatment_vs_control'] = {
                    'change': change,
                    'change_percent': round(change_percent, 2)
                }

        return result

    def _extract_metric_value(self, data: Dict, metric_name: str) -> float:
        """Extract metric value from API response."""
        if not data or 'data' not in data or not data['data']:
            return 0.0

        # Sum metric across all rows
        total = 0
        for row in data['data']:
            if metric_name in row:
                total += float(row[metric_name])

        return total

    def _extract_metric_for_videos(
        self,
        data: Dict,
        metric_name: str,
        video_ids: List[str]
    ) -> float:
        """Extract metric value for specific videos."""
        if not data or 'data' not in data:
            return 0.0

        total = 0
        for row in data['data']:
            if 'video' in row and row['video'] in video_ids:
                if metric_name in row:
                    total += float(row[metric_name])

        return total

    def _check_success_criteria(
        self,
        metric_result: Dict,
        criteria: 'SuccessCriteria'
    ) -> bool:
        """
        Determine if experiment met success criteria using COMPOUNDING logic.
        
        For sequential experiments:
        - Success requires beating control by the threshold percentage
        - Uses compound growth: each experiment must beat previous result
        - Not simple comparison to fixed baseline
        
        Formula: Treatment >= Control × (1 + threshold/100)
        
        Example with 5% threshold:
        - Control: 100 subs
        - Target: 100 × 1.05 = 105 subs
        - Treatment must be >= 105 for success
        """
        # Get actual values (not percentages)
        if 'treatment_vs_control' in metric_result:
            treatment_value = metric_result.get('treatment_value', 0)
            control_value = metric_result.get('control_value', 0)
        elif metric_result['change_percent'] is not None:
            treatment_value = metric_result.get('experiment_value', 0)
            control_value = metric_result.get('baseline_value', 0)
        else:
            return False
        
        # Need control value to calculate compound target
        if not control_value or control_value == 0:
            # Fallback to percentage comparison if no control value
            if 'treatment_vs_control' in metric_result:
                change_percent = metric_result['treatment_vs_control']['change_percent']
            elif metric_result['change_percent'] is not None:
                change_percent = metric_result['change_percent']
            else:
                return False
            
            # Use simple percentage comparison as fallback
            operator = criteria.operator
            threshold = criteria.threshold
            
            if operator == ComparisonOperator.INCREASE:
                return change_percent >= threshold
            elif operator == ComparisonOperator.DECREASE:
                return change_percent <= -threshold
            else:
                return False
        
        # COMPOUND GROWTH LOGIC
        operator = criteria.operator
        threshold = criteria.threshold
        
        if operator == ComparisonOperator.INCREASE:
            # Calculate compound target: Control × (1 + threshold/100)
            compound_target = control_value * (1 + threshold / 100)
            success = treatment_value >= compound_target
            
            # Add debug info to result
            metric_result['compound_target'] = round(compound_target, 2)
            metric_result['compound_success'] = success
            
            return success
            
        elif operator == ComparisonOperator.DECREASE:
            # For decrease: Treatment must be <= Control × (1 - threshold/100)
            compound_target = control_value * (1 - threshold / 100)
            success = treatment_value <= compound_target
            
            metric_result['compound_target'] = round(compound_target, 2)
            metric_result['compound_success'] = success
            
            return success
            
        elif operator == ComparisonOperator.EQUALS:
            # For equals: Treatment must be within 1% of target
            target_value = control_value * (1 + threshold / 100)
            tolerance = control_value * 0.01  # 1% tolerance
            return abs(treatment_value - target_value) < tolerance
            
        elif operator == ComparisonOperator.GREATER_THAN:
            # Absolute comparison
            return treatment_value > control_value * (1 + threshold / 100)
            
        elif operator == ComparisonOperator.LESS_THAN:
            # Absolute comparison
            return treatment_value < control_value * (1 + threshold / 100)

        return False

    def _generate_conclusion(self, analysis: Dict, experiment: Experiment) -> str:
        """Generate human-readable conclusion from analysis."""
        primary_metric = experiment.metrics['primary']
        metric_result = analysis['metrics'][primary_metric]

        # Build conclusion
        parts = []

        if analysis['success']:
            parts.append(f"✓ Experiment successful: {experiment.hypothesis}")
        else:
            parts.append(f"✗ Experiment unsuccessful: {experiment.hypothesis}")

        # Primary metric details with actual values
        if 'treatment_vs_control' in metric_result:
            treatment_val = metric_result.get('treatment_value', 0)
            control_val = metric_result.get('control_value', 0)
            change = metric_result['treatment_vs_control']['change_percent']
            
            parts.append(
                f"\nTreatment: {treatment_val:.1f} {primary_metric} "
                f"vs Control: {control_val:.1f} {primary_metric} "
                f"({change:+.1f}% change)"
            )
            
            # Show compound target if available
            if 'compound_target' in metric_result:
                target = metric_result['compound_target']
                parts.append(
                    f"\nCompound Target: {target:.1f} {primary_metric} "
                    f"(control × 1.{experiment.success_criteria.threshold/100:.2f})"
                )
                if treatment_val >= target:
                    parts.append(f"✓ Achieved: {treatment_val:.1f} >= {target:.1f}")
                else:
                    parts.append(f"✗ Missed: {treatment_val:.1f} < {target:.1f}")
        
        elif metric_result['change_percent'] is not None:
            change = metric_result['change_percent']
            parts.append(
                f"\n{primary_metric.capitalize()} changed by {change:+.1f}% "
                f"compared to baseline."
            )

        # Success criteria explanation
        criteria = experiment.success_criteria
        parts.append(
            f"\nThreshold: {criteria.threshold}% {criteria.operator.value} in {criteria.metric}"
        )

        return ' '.join(parts)
