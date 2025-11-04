"""Export experiment results to various formats (PDF, CSV, Excel)."""

import csv
import json
from typing import Dict, List
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, PageBreak, Image
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not available. Using matplotlib for charts. Install with: pip install plotly kaleido")


class ExportManager:
    """Manage exports of experiment results to various formats."""
    
    def __init__(self, output_dir: str = "exports"):
        """Initialize export manager."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_to_csv(
        self,
        analysis: Dict,
        filename: str = None
    ) -> str:
        """
        Export experiment results to CSV format.
        
        Args:
            analysis: Analysis results dictionary
            filename: Output filename (auto-generated if None)
        
        Returns:
            Path to created CSV file
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"experiment_{analysis['experiment_id']}_{timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header information
            writer.writerow(['Experiment Analysis Report'])
            writer.writerow(['Generated:', analysis['analysis_date']])
            writer.writerow([])
            
            # Experiment details
            writer.writerow(['Experiment ID:', analysis['experiment_id']])
            writer.writerow(['Name:', analysis['experiment_name']])
            writer.writerow(['Hypothesis:', analysis['hypothesis']])
            writer.writerow(['Period:', analysis['period']['experiment']])
            if analysis['period'].get('comparison'):
                writer.writerow(['Comparison Period:', analysis['period']['comparison']])
            writer.writerow(['Success:', 'Yes' if analysis['success'] else 'No'])
            writer.writerow([])
            
            # Metrics table
            writer.writerow(['Metrics Results'])
            writer.writerow([
                'Metric',
                'Experiment Value',
                'Comparison Value',
                'Change',
                'Change %'
            ])
            
            for metric_name, metric_data in analysis['metrics'].items():
                writer.writerow([
                    metric_name,
                    metric_data.get('experiment_value', ''),
                    metric_data.get('comparison_value', ''),
                    metric_data.get('change', ''),
                    f"{metric_data.get('change_percent', 0):.2f}%" if metric_data.get('change_percent') is not None else ''
                ])
            
            writer.writerow([])
            writer.writerow(['Conclusion:', analysis['conclusion']])
        
        return str(output_path)
    
    def export_metrics_to_csv(
        self,
        analysis: Dict,
        filename: str = None
    ) -> str:
        """Export just the metrics data to CSV (for further analysis)."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"metrics_{analysis['experiment_id']}_{timestamp}.csv"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', newline='') as csvfile:
            # Get all unique fields from metrics
            fieldnames = ['metric_name']
            if analysis['metrics']:
                first_metric = list(analysis['metrics'].values())[0]
                fieldnames.extend(first_metric.keys())
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for metric_name, metric_data in analysis['metrics'].items():
                row = {'metric_name': metric_name}
                row.update(metric_data)
                writer.writerow(row)
        
        return str(output_path)
    
    def export_to_pdf(
        self,
        analysis: Dict,
        filename: str = None,
        include_charts: bool = True
    ) -> str:
        """
        Export experiment results to PDF format.
        
        Args:
            analysis: Analysis results dictionary
            filename: Output filename (auto-generated if None)
            include_charts: Whether to include visualization charts
        
        Returns:
            Path to created PDF file
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError(
                "reportlab is required for PDF export. "
                "Install with: pip install reportlab"
            )
        
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{analysis['experiment_id']}_{timestamp}.pdf"
        
        output_path = self.output_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        story = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        story.append(Paragraph("Experiment Analysis Report", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Experiment details
        story.append(Paragraph(f"<b>Experiment:</b> {analysis['experiment_name']}", styles['Normal']))
        story.append(Paragraph(f"<b>ID:</b> {analysis['experiment_id']}", styles['Normal']))
        story.append(Paragraph(f"<b>Generated:</b> {analysis['analysis_date']}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Hypothesis
        story.append(Paragraph("<b>Hypothesis</b>", styles['Heading2']))
        story.append(Paragraph(analysis['hypothesis'], styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Period
        story.append(Paragraph("<b>Test Period</b>", styles['Heading2']))
        story.append(Paragraph(f"Experiment: {analysis['period']['experiment']}", styles['Normal']))
        if analysis['period'].get('comparison'):
            story.append(Paragraph(f"Comparison: {analysis['period']['comparison']}", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
        
        # Success status
        success_text = "✓ SUCCESS" if analysis['success'] else "✗ UNSUCCESSFUL"
        success_color = colors.green if analysis['success'] else colors.red
        success_style = ParagraphStyle(
            'SuccessStyle',
            parent=styles['Normal'],
            fontSize=16,
            textColor=success_color,
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph(success_text, success_style))
        story.append(Spacer(1, 0.1 * inch))
        
        # Conclusion
        story.append(Paragraph("<b>Conclusion</b>", styles['Heading2']))
        story.append(Paragraph(analysis['conclusion'], styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))
        
        # Metrics table
        story.append(Paragraph("<b>Detailed Metrics</b>", styles['Heading2']))
        
        metrics_data = [['Metric', 'Experiment', 'Comparison', 'Change %']]
        
        for metric_name, metric_data in analysis['metrics'].items():
            exp_val = self._format_metric_value(metric_data.get('experiment_value', 0))
            comp_val = self._format_metric_value(metric_data.get('comparison_value', 0))
            change = metric_data.get('change_percent')
            change_str = f"{change:+.1f}%" if change is not None else 'N/A'
            
            metrics_data.append([
                metric_name,
                exp_val,
                comp_val,
                change_str
            ])
        
        table = Table(metrics_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Add charts if requested
        if include_charts and analysis['metrics']:
            story.append(PageBreak())
            story.append(Paragraph("<b>Visualizations</b>", styles['Heading2']))
            
            chart_path = self._create_metrics_chart(analysis)
            if chart_path:
                img = Image(chart_path, width=6*inch, height=4*inch)
                story.append(img)
        
        # Statistical significance if available
        if analysis.get('statistical_significance'):
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("<b>Statistical Analysis</b>", styles['Heading2']))
            
            sig = analysis['statistical_significance']
            story.append(Paragraph(
                f"Statistical Significance: {'Yes' if sig.get('is_significant') else 'No'}",
                styles['Normal']
            ))
            story.append(Paragraph(
                f"P-value: {sig.get('p_value', 'N/A')}",
                styles['Normal']
            ))
            story.append(Paragraph(
                f"Effect Size: {sig.get('effect_size', 'N/A')}",
                styles['Normal']
            ))
        
        # Build PDF
        doc.build(story)
        
        return str(output_path)
    
    def _create_metrics_chart(self, analysis: Dict) -> str:
        """Create a bar chart comparing metrics. Uses Plotly if available, falls back to matplotlib."""
        metrics = analysis['metrics']
        
        if not metrics:
            return None
        
        # Prepare data
        metric_names = []
        experiment_values = []
        comparison_values = []
        
        for name, data in metrics.items():
            metric_names.append(name[:30])  # Truncate long names
            experiment_values.append(data.get('experiment_value', 0))
            comp_val = data.get('comparison_value') or data.get('control_value') or data.get('baseline_value') or 0
            comparison_values.append(comp_val)
        
        # Use Plotly if available for better interactive charts
        if PLOTLY_AVAILABLE:
            try:
                fig = go.Figure()
                
                # Add experiment bars
                fig.add_trace(go.Bar(
                    name='Treatment',
                    x=metric_names,
                    y=experiment_values,
                    marker_color='#4CAF50',
                    text=[f'{v:,.0f}' if v < 1000 else f'{v/1000:.1f}K' for v in experiment_values],
                    textposition='outside'
                ))
                
                # Add control/comparison bars
                fig.add_trace(go.Bar(
                    name='Control',
                    x=metric_names,
                    y=comparison_values,
                    marker_color='#2196F3',
                    text=[f'{v:,.0f}' if v < 1000 else f'{v/1000:.1f}K' for v in comparison_values],
                    textposition='outside'
                ))
                
                fig.update_layout(
                    title=f"Experiment: {analysis['experiment_name']} - Metrics Comparison",
                    xaxis_title='Metrics',
                    yaxis_title='Values',
                    barmode='group',
                    hovermode='x unified',
                    template='plotly_white',
                    height=500,
                    width=1000,
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Save as PNG for PDF inclusion
                chart_path = self.output_dir / f"chart_{analysis['experiment_id']}.png"
                pio.write_image(fig, str(chart_path), width=1000, height=500, scale=2)
                
                # Also save as HTML for interactive viewing
                html_path = self.output_dir / f"chart_{analysis['experiment_id']}.html"
                fig.write_html(str(html_path))
                
                return str(chart_path)
            except Exception as e:
                print(f"Warning: Could not create Plotly chart ({e}), falling back to matplotlib")
                # Fall through to matplotlib implementation
        
        # Fallback to matplotlib
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(metric_names))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], experiment_values, width, label='Treatment', color='#4CAF50')
        ax.bar([i + width/2 for i in x], comparison_values, width, label='Control', color='#2196F3')
        
        ax.set_xlabel('Metrics')
        ax.set_ylabel('Values')
        ax.set_title('Experiment vs Comparison Metrics')
        ax.set_xticks(x)
        ax.set_xticklabels(metric_names, rotation=45, ha='right')
        ax.legend()
        
        plt.tight_layout()
        
        # Save chart
        chart_path = self.output_dir / f"chart_{analysis['experiment_id']}.png"
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(chart_path)
    
    def _format_metric_value(self, value) -> str:
        """Format metric value for display."""
        if value is None or value == '-':
            return 'N/A'
        
        if isinstance(value, (int, float)):
            if value >= 1000000:
                return f"{value/1000000:.2f}M"
            elif value >= 1000:
                return f"{value/1000:.2f}K"
            else:
                return f"{value:.1f}"
        
        return str(value)
    
    def export_comparison_csv(
        self,
        analyses: List[Dict],
        filename: str = "experiments_comparison.csv"
    ) -> str:
        """Export comparison of multiple experiments to CSV."""
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow(['Experiments Comparison'])
            writer.writerow(['Generated:', datetime.now().isoformat()])
            writer.writerow([])
            
            # Table header
            writer.writerow([
                'Experiment ID',
                'Name',
                'Success',
                'Primary Metric',
                'Change %',
                'Period'
            ])
            
            for analysis in analyses:
                primary_metric = list(analysis['metrics'].keys())[0]
                metric_data = analysis['metrics'][primary_metric]
                change = metric_data.get('change_percent', 0)
                
                writer.writerow([
                    analysis['experiment_id'],
                    analysis['experiment_name'],
                    'Yes' if analysis['success'] else 'No',
                    primary_metric,
                    f"{change:+.1f}%",
                    analysis['period']['experiment']
                ])
        
        return str(output_path)





