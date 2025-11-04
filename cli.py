#!/usr/bin/env python3
"""Command-line interface for YouTube experiment management."""

import sys
import argparse
from datetime import datetime
from typing import Optional

from experiment_manager import (
    ExperimentManager, Experiment, ExperimentStatus,
    SuccessCriteria, ComparisonOperator
)
from youtube_analytics import YouTubeAnalytics
from experiment_analyser import ExperimentAnalyser
from report_generator import ReportGenerator


class ExperimentCLI:
    """CLI for managing YouTube analytics experiments."""

    def __init__(self):
        self.manager = ExperimentManager()
        self.youtube = None
        self.analyser = None
        self.reporter = ReportGenerator()

    def _init_youtube(self):
        """Initialise YouTube API connection (lazy load)."""
        if not self.youtube:
            self.youtube = YouTubeAnalytics()
            self.analyser = ExperimentAnalyser(self.youtube, self.manager)

    def create_experiment(self, args):
        """Create a new experiment."""
        # Build success criteria
        success_criteria = SuccessCriteria(
            metric=args.success_metric,
            threshold=args.success_threshold,
            operator=ComparisonOperator(args.success_operator)
        )

        # Build metrics configuration
        metrics = {
            'primary': args.primary_metric,
            'secondary': args.secondary_metrics.split(',') if args.secondary_metrics else []
        }

        # Build video IDs if provided
        video_ids = None
        if args.treatment_videos or args.control_videos:
            video_ids = {}
            if args.treatment_videos:
                video_ids['treatment'] = args.treatment_videos.split(',')
            if args.control_videos:
                video_ids['control'] = args.control_videos.split(',')

        experiment = Experiment(
            id=args.id,
            name=args.name,
            hypothesis=args.hypothesis,
            start_date=args.start_date,
            end_date=args.end_date,
            baseline_start=args.baseline_start,
            baseline_end=args.baseline_end,
            metrics=metrics,
            success_criteria=success_criteria,
            video_ids=video_ids,
            notes=args.notes or ""
        )

        exp_id = self.manager.create_experiment(experiment)
        print(f"Created experiment: {exp_id}")
        print(f"Name: {experiment.name}")
        print(f"Period: {experiment.start_date} to {experiment.end_date}")
        print(f"Status: {experiment.status.value}")

    def list_experiments(self, args):
        """List experiments."""
        status = ExperimentStatus(args.status) if args.status else None
        experiments = self.manager.list_experiments(status)

        if not experiments:
            print("No experiments found.")
            return

        print(f"\nFound {len(experiments)} experiment(s):\n")

        for exp in experiments:
            active_marker = "▶ " if exp.is_active() else "  "
            ready_marker = "✓ " if exp.is_ready_for_analysis() else "  "

            print(f"{active_marker}{ready_marker}{exp.id}")
            print(f"  Name: {exp.name}")
            print(f"  Status: {exp.status.value}")
            print(f"  Period: {exp.start_date} to {exp.end_date}")
            print(f"  Hypothesis: {exp.hypothesis}")
            print()

    def show_experiment(self, args):
        """Show detailed experiment information."""
        exp = self.manager.get_experiment(args.id)

        if not exp:
            print(f"Experiment {args.id} not found.")
            return

        print(f"\nExperiment: {exp.name}")
        print(f"ID: {exp.id}")
        print(f"Status: {exp.status.value}")
        print(f"\nHypothesis: {exp.hypothesis}")
        print(f"\nPeriod:")
        print(f"  Experiment: {exp.start_date} to {exp.end_date}")
        if exp.baseline_start:
            print(f"  Baseline: {exp.baseline_start} to {exp.baseline_end}")

        print(f"\nMetrics:")
        print(f"  Primary: {exp.metrics['primary']}")
        if exp.metrics.get('secondary'):
            print(f"  Secondary: {', '.join(exp.metrics['secondary'])}")

        print(f"\nSuccess Criteria:")
        print(f"  {exp.success_criteria.metric} must {exp.success_criteria.operator.value}")
        print(f"  by {exp.success_criteria.threshold}%")

        if exp.video_ids:
            print(f"\nVideo Groups:")
            if 'treatment' in exp.video_ids:
                print(f"  Treatment: {', '.join(exp.video_ids['treatment'])}")
            if 'control' in exp.video_ids:
                print(f"  Control: {', '.join(exp.video_ids['control'])}")

        if exp.notes:
            print(f"\nNotes: {exp.notes}")

        print(f"\nCreated: {exp.created_at}")

        if exp.is_active():
            print("\n▶ Currently active")
        if exp.is_ready_for_analysis():
            print("✓ Ready for analysis")

    # Start/Stop methods removed - status is now automatic based on dates

    def analyse_experiment(self, args):
        """Analyse experiment results."""
        self._init_youtube()

        exp = self.manager.get_experiment(args.id)
        if not exp:
            print(f"Experiment {args.id} not found.")
            return

        print(f"Analysing experiment: {exp.name}...")

        try:
            analysis = self.analyser.analyse_experiment(exp)

            # Save results to experiment
            self.manager.update_experiment(args.id, {'results': analysis})

            # Generate and display report
            if args.format == 'json':
                report = self.reporter.generate_json_report(analysis)
            elif args.format == 'summary':
                report = self.reporter.generate_summary(analysis)
            else:
                report = self.reporter.generate_text_report(analysis)

            print("\n" + report)

            # Save to file if requested
            if args.output:
                self.reporter.save_report(analysis, args.output, args.format)
                print(f"\nReport saved to: {args.output}")

        except Exception as e:
            print(f"Error analysing experiment: {e}")
            import traceback
            traceback.print_exc()

    def analyse_all_ready(self, args):
        """Analyse all experiments ready for analysis."""
        self._init_youtube()

        ready = self.manager.get_ready_for_analysis()

        if not ready:
            print("No experiments ready for analysis.")
            return

        print(f"Found {len(ready)} experiment(s) ready for analysis.\n")

        analyses = []
        for exp in ready:
            print(f"Analysing: {exp.name}...")
            try:
                analysis = self.analyser.analyse_experiment(exp)
                analyses.append(analysis)

                # Save results
                self.manager.update_experiment(exp.id, {'results': analysis})

                print(self.reporter.generate_summary(analysis))
                print()

            except Exception as e:
                print(f"Error analysing {exp.id}: {e}\n")

        # Show comparison table
        if analyses:
            print("\nComparison Table:")
            print(self.reporter.generate_comparison_table(analyses))

    def delete_experiment(self, args):
        """Delete an experiment."""
        if not args.force:
            confirm = input(f"Delete experiment {args.id}? (y/N): ")
            if confirm.lower() != 'y':
                print("Cancelled.")
                return

        self.manager.delete_experiment(args.id)
        print(f"Deleted experiment {args.id}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='YouTube Analytics Experiment Manager',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Create experiment
    create_parser = subparsers.add_parser('create', help='Create new experiment')
    create_parser.add_argument('--id', required=True, help='Experiment ID')
    create_parser.add_argument('--name', required=True, help='Experiment name')
    create_parser.add_argument('--hypothesis', required=True, help='Hypothesis statement')
    create_parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
    create_parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
    create_parser.add_argument('--baseline-start', help='Baseline start date (YYYY-MM-DD)')
    create_parser.add_argument('--baseline-end', help='Baseline end date (YYYY-MM-DD)')
    create_parser.add_argument('--primary-metric', required=True, help='Primary metric to track')
    create_parser.add_argument('--secondary-metrics', help='Secondary metrics (comma-separated)')
    create_parser.add_argument('--success-metric', required=True, help='Metric for success criteria')
    create_parser.add_argument('--success-threshold', type=float, required=True, help='Success threshold (percent)')
    create_parser.add_argument('--success-operator', required=True,
                              choices=['increase', 'decrease', 'equals', 'greater_than', 'less_than'],
                              help='Success operator')
    create_parser.add_argument('--treatment-videos', 
                              help='Treatment video IDs (comma-separated). Optional - if not specified, automatically uses all videos published between start-date and end-date')
    create_parser.add_argument('--control-videos', 
                              help='Control video IDs (comma-separated). Optional - if not specified, automatically uses all videos published before start-date')
    create_parser.add_argument('--notes', help='Additional notes')

    # List experiments
    list_parser = subparsers.add_parser('list', help='List experiments')
    list_parser.add_argument('--status', choices=['draft', 'active', 'completed', 'cancelled'],
                            help='Filter by status')

    # Show experiment
    show_parser = subparsers.add_parser('show', help='Show experiment details')
    show_parser.add_argument('id', help='Experiment ID')

    # Start/Stop commands removed - status is now automatic based on dates
    # Experiments are automatically:
    # - DRAFT if start_date is in the future
    # - ACTIVE if currently within the date range
    # - COMPLETED if end_date has passed

    # Analyse experiment
    analyse_parser = subparsers.add_parser('analyse', help='Analyse experiment results')
    analyse_parser.add_argument('id', help='Experiment ID')
    analyse_parser.add_argument('--format', choices=['text', 'json', 'summary'], default='text',
                               help='Report format')
    analyse_parser.add_argument('--output', help='Save report to file')

    # Analyse all ready
    subparsers.add_parser('analyse-all', help='Analyse all experiments ready for analysis')

    # Delete experiment
    delete_parser = subparsers.add_parser('delete', help='Delete experiment')
    delete_parser.add_argument('id', help='Experiment ID')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = ExperimentCLI()

    # Route to appropriate method
    command_map = {
        'create': cli.create_experiment,
        'list': cli.list_experiments,
        'show': cli.show_experiment,
        'analyse': cli.analyse_experiment,
        'analyse-all': cli.analyse_all_ready,
        'delete': cli.delete_experiment,
    }

    handler = command_map.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
