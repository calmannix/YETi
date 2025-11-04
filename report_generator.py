"""Generate reports and visualisations for experiment results."""

import json
from typing import Dict, List
from datetime import datetime
from tabulate import tabulate


class ReportGenerator:
    """Create formatted reports from experiment analysis."""

    def generate_text_report(self, analysis: Dict) -> str:
        """Generate formatted text report."""
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(f"EXPERIMENT ANALYSIS REPORT")
        lines.append("=" * 80)
        lines.append(f"\nExperiment: {analysis['experiment_name']}")
        lines.append(f"ID: {analysis['experiment_id']}")
        lines.append(f"Analysis Date: {analysis['analysis_date']}")
        lines.append(f"\nHypothesis: {analysis['hypothesis']}")

        # Period
        lines.append(f"\nPeriod:")
        if analysis['period'].get('comparison'):
            lines.append(f"  Comparison: {analysis['period']['comparison']}")
        lines.append(f"  Experiment: {analysis['period']['experiment']}")

        # Results
        lines.append(f"\n{'SUCCESS' if analysis['success'] else 'UNSUCCESSFUL'}")
        lines.append(f"\n{analysis['conclusion']}")

        # Metrics table
        lines.append(f"\n\nDetailed Metrics:")
        lines.append("-" * 80)

        metrics_data = []
        for metric_name, metric_data in analysis['metrics'].items():
            row = {
                'Metric': metric_name,
                'Experiment': self._format_number(metric_data['experiment_value']),
                'Comparison': self._format_number(metric_data.get('comparison_value', '-')),
                'Change': self._format_change(metric_data.get('change_percent'))
            }

            # Add treatment vs control if available
            if 'treatment_vs_control' in metric_data:
                row['Treatment'] = self._format_number(metric_data['treatment_value'])
                row['Control'] = self._format_number(metric_data['control_value'])
                row['T vs C'] = self._format_change(
                    metric_data['treatment_vs_control']['change_percent']
                )

            metrics_data.append(row)

        lines.append(tabulate(metrics_data, headers='keys', tablefmt='grid'))

        lines.append("\n" + "=" * 80)

        return '\n'.join(lines)

    def generate_summary(self, analysis: Dict) -> str:
        """Generate brief summary of results."""
        primary_metric = list(analysis['metrics'].keys())[0]
        metric_data = analysis['metrics'][primary_metric]

        status = "✓ Success" if analysis['success'] else "✗ Unsuccessful"

        if 'treatment_vs_control' in metric_data:
            change = metric_data['treatment_vs_control']['change_percent']
        else:
            change = metric_data.get('change_percent', 0)

        summary = (
            f"{status} - {analysis['experiment_name']}\n"
            f"  {primary_metric}: {change:+.1f}%\n"
            f"  {analysis['conclusion']}"
        )

        return summary

    def generate_json_report(self, analysis: Dict) -> str:
        """Generate JSON format report."""
        return json.dumps(analysis, indent=2)

    def generate_comparison_table(self, analyses: List[Dict]) -> str:
        """Compare multiple experiments in a table."""
        if not analyses:
            return "No experiments to compare."

        rows = []
        for analysis in analyses:
            # Get primary metric
            primary_metric = list(analysis['metrics'].keys())[0]
            metric_data = analysis['metrics'][primary_metric]

            if 'treatment_vs_control' in metric_data:
                change = metric_data['treatment_vs_control']['change_percent']
            else:
                change = metric_data.get('change_percent', 0)

            rows.append({
                'ID': analysis['experiment_id'],
                'Name': analysis['experiment_name'],
                'Status': '✓' if analysis['success'] else '✗',
                'Primary Metric': primary_metric,
                'Change': self._format_change(change),
                'Period': analysis['period']['experiment']
            })

        return tabulate(rows, headers='keys', tablefmt='grid')

    def _format_number(self, value) -> str:
        """Format number for display."""
        if value == '-' or value is None:
            return '-'

        if isinstance(value, (int, float)):
            if value >= 1000000:
                return f"{value/1000000:.2f}M"
            elif value >= 1000:
                return f"{value/1000:.2f}K"
            else:
                return f"{value:.1f}"

        return str(value)

    def _format_change(self, percent) -> str:
        """Format percentage change for display."""
        if percent is None:
            return '-'

        sign = '+' if percent >= 0 else ''
        return f"{sign}{percent:.1f}%"

    def save_report(self, analysis: Dict, output_file: str, format: str = 'text'):
        """Save report to file."""
        if format == 'text':
            content = self.generate_text_report(analysis)
        elif format == 'json':
            content = self.generate_json_report(analysis)
        else:
            raise ValueError(f"Unknown format: {format}")

        with open(output_file, 'w') as f:
            f.write(content)

        return output_file
