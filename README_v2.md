# 👹 YETi v2.0 - YouTube Experiment Testing intelligence

A comprehensive A/B testing and analytics tool for YouTube content creators. Test thumbnails, titles, upload times, and more with statistical significance testing and beautiful visualizations.

## 🎯 What's New in v2.0

### Enhanced Features
- ✅ **Statistical Significance Testing** - Know if your results are meaningful
- ✅ **Video Variant Management** - Track A/B test variations for thumbnails, titles, etc.
- ✅ **PDF & CSV Exports** - Professional reports with charts
- ✅ **Web Dashboard** - Modern UI for managing experiments
- ✅ **REST API** - Programmatic access to all features
- ✅ **Real-time Monitoring** - Track experiment progress live
- ✅ **Enhanced Analytics** - Confidence intervals, effect sizes, power analysis

### Backward Compatible
All existing CLI commands and YAML configurations still work!

## 📦 Installation

### Quick Start

```bash
# Clone or navigate to the repository
cd path/to/YETi

# Activate virtual environment
source venv/bin/activate

# Install new dependencies
pip install -r requirements.txt

# Start the web server
python start_server.py
```

The dashboard will automatically open in your browser at `http://localhost:5000`

## 🚀 Usage

### Option 1: Web Dashboard (New!)

1. **Start the server:**
   ```bash
   python start_server.py
   ```

2. **Open your browser** to http://localhost:5000

3. **Use the dashboard to:**
   - View all experiments
   - Create and manage experiments
   - Run analyses with one click
   - View beautiful reports
   - Export to PDF/CSV

### Option 2: Command Line (Still Available!)

All existing CLI commands work exactly as before:

```bash
# List experiments
python cli.py list

# Create experiment
python cli.py create --id exp_001 --name "Test" ...

# Analyze
python cli.py analyse exp_001

# Use markdown workflow
python run_experiment.py my_experiment.md
```

### Option 3: REST API

Access programmatically:

```python
import requests

# Get all experiments
response = requests.get('http://localhost:5000/api/experiments')
experiments = response.json()

# Analyze experiment
response = requests.post('http://localhost:5000/api/experiments/exp_001/analyze')
analysis = response.json()
```

## 📊 New Features Guide

### 1. Statistical Significance Testing

Automatically calculates:
- **P-values** - Probability results are due to chance
- **Effect size** - Magnitude of the difference
- **Statistical power** - Ability to detect real effects
- **Confidence intervals** - Range of likely true values

```python
from statistics_engine import StatisticsEngine

engine = StatisticsEngine(confidence_level=0.95)

# Compare two variants
result = engine.z_test_proportions(
    successes1=150,  # Treatment clicks
    total1=1000,     # Treatment impressions
    successes2=100,  # Control clicks
    total2=1000      # Control impressions
)

print(f"Significant: {result.is_significant}")
print(f"P-value: {result.p_value}")
print(f"Effect size: {result.effect_size}")
```

### 2. Video Variants

Track different versions of video elements:

```python
from models.variant import VideoVariant, VariantType

# Create thumbnail variant
variant = VideoVariant(
    id="var_001",
    experiment_id="exp_001",
    variant_type=VariantType.THUMBNAIL,
    name="Bold Red Thumbnail",
    description="High contrast with red background",
    video_ids=["VIDEO_ID_1", "VIDEO_ID_2"],
    traffic_allocation=50.0  # 50% of traffic
)
```

Variant types supported:
- Thumbnails
- Titles
- Descriptions
- Upload times
- Video lengths
- Intros/Outros
- Tags
- Custom

### 3. Export Reports

#### PDF Export (with charts!)

```python
from export_manager import ExportManager

exporter = ExportManager(output_dir="exports")

# Export to PDF with visualizations
pdf_path = exporter.export_to_pdf(
    analysis=analysis_results,
    include_charts=True
)
```

#### CSV Export

```python
# Export full report to CSV
csv_path = exporter.export_to_csv(analysis_results)

# Export just metrics data
metrics_path = exporter.export_metrics_to_csv(analysis_results)

# Compare multiple experiments
comparison_path = exporter.export_comparison_csv([analysis1, analysis2, analysis3])
```

### 4. Enhanced Experiment Model

Create experiments with more control:

```python
from models.experiment_enhanced import EnhancedExperiment

exp = EnhancedExperiment(
    id="exp_001",
    name="Thumbnail A/B Test",
    hypothesis="Red thumbnails increase CTR by 20%",
    start_date="2025-10-22",
    end_date="2025-11-05",
    metrics={'primary': 'impressionClickThroughRate', 'secondary': ['views']},
    success_criteria=success_criteria,
    
    # New fields
    sample_size_target=10000,  # Target impressions
    confidence_level=0.95,      # 95% confidence
    auto_stop_on_significance=True,  # Stop when significant
    auto_pick_winner=True       # Auto-declare winner
)

# Track progress
progress = exp.calculate_progress()  # Returns percentage complete
```

## 🌐 API Reference

### Experiments

```http
GET    /api/experiments              List all experiments
POST   /api/experiments              Create experiment
GET    /api/experiments/:id          Get experiment details
PUT    /api/experiments/:id          Update experiment
DELETE /api/experiments/:id          Delete experiment
POST   /api/experiments/:id/start    Start experiment
POST   /api/experiments/:id/stop     Stop experiment
POST   /api/experiments/:id/analyze  Run analysis
GET    /api/experiments/:id/report   Get report
POST   /api/experiments/:id/export   Export to file
```

### Dashboard

```http
GET    /api/dashboard/summary        Get dashboard stats
```

### Variants

```http
POST   /api/variants                 Create variant
GET    /api/variants/:experiment_id  Get variants
```

### Statistics

```http
POST   /api/statistics/significance  Calculate significance
POST   /api/statistics/sample-size   Calculate required sample size
```

### System

```http
GET    /api/health                   Health check
```

## 📈 Example Workflow

### Complete A/B Test Example

```python
# 1. Create experiment with variants
exp = EnhancedExperiment(
    id="thumb_test_001",
    name="Thumbnail Style Test",
    hypothesis="Bold thumbnails increase CTR",
    start_date="2025-10-22",
    end_date="2025-11-05",
    metrics={'primary': 'impressionClickThroughRate'},
    success_criteria=SuccessCriteria(
        metric='impressionClickThroughRate',
        threshold=15.0,  # 15% improvement
        operator=ComparisonOperator.INCREASE
    ),
    sample_size_target=5000
)

# 2. Add variants
variant_a = VideoVariant(
    id="var_control",
    experiment_id="thumb_test_001",
    variant_type=VariantType.THUMBNAIL,
    name="Original Thumbnail",
    is_control=True,
    video_ids=["VIDEO_1", "VIDEO_2"]
)

variant_b = VideoVariant(
    id="var_treatment",
    experiment_id="thumb_test_001",
    variant_type=VariantType.THUMBNAIL,
    name="Bold Red Thumbnail",
    video_ids=["VIDEO_3", "VIDEO_4"]
)

exp.add_variant(variant_a)
exp.add_variant(variant_b)

# 3. Run experiment (upload videos with different thumbnails)

# 4. Analyze results
from experiment_analyser import ExperimentAnalyser
from youtube_analytics import YouTubeAnalytics

youtube = YouTubeAnalytics()
analyser = ExperimentAnalyser(youtube)

analysis = analyser.analyse_experiment(exp)

# 5. Check statistical significance
if analysis['statistical_significance']['is_significant']:
    print(f"✓ Significant result! P-value: {analysis['statistical_significance']['p_value']}")
    print(f"Effect size: {analysis['statistical_significance']['effect_size']}")
else:
    print("No significant difference found. Need more data.")

# 6. Export report
from export_manager import ExportManager

exporter = ExportManager()
pdf_path = exporter.export_to_pdf(analysis, include_charts=True)
print(f"Report saved to: {pdf_path}")
```

## 🔧 Configuration

### Environment Variables

```bash
# Server configuration
export PORT=5000
export DEBUG=True

# Data directories
export EXPERIMENTS_FILE=experiments.yaml
export EXPORTS_DIR=exports
```

### Files

- `experiments.yaml` - Experiment storage (automatically created)
- `credentials.json` - YouTube API credentials
- `token.pickle` - OAuth token (auto-generated)
- `exports/` - Generated reports (auto-created)

## 📊 Statistical Methods

### Tests Available

1. **Two-Sample T-Test (Welch's t-test)**
   - For continuous metrics (view duration, watch time)
   - Handles unequal variances
   - Returns p-value, effect size (Cohen's d), statistical power

2. **Z-Test for Proportions**
   - For rate metrics (CTR, conversion rate)
   - Compares two proportions
   - Returns p-value, effect size (Cohen's h)

3. **Confidence Intervals**
   - Provides range of likely true values
   - Adjustable confidence level (default 95%)

4. **Sample Size Calculation**
   - Determines minimum samples needed
   - Based on expected effect size
   - Ensures adequate statistical power

### Interpreting Results

**P-value:**
- < 0.05: Statistically significant (95% confidence)
- < 0.01: Highly significant (99% confidence)
- ≥ 0.05: Not significant, could be chance

**Effect Size:**
- < 0.2: Small effect
- 0.2 - 0.5: Medium effect
- > 0.5: Large effect

**Statistical Power:**
- > 0.80: Good (80% chance of detecting real effect)
- < 0.80: Need more samples

## 🎨 Dashboard Features

### Main View
- **Stats Overview** - Total experiments, active, success rate
- **Experiment List** - All experiments with status
- **Quick Actions** - Start, stop, analyze, delete

### Experiment Card
- Visual status indicator (Active, Completed, Draft)
- Success/failure icon
- Quick action buttons
- Period and hypothesis display

### Reports
- View inline or download
- Charts and visualizations
- Statistical analysis summary

## 🔍 Troubleshooting

### API Not Starting

```bash
# Check if dependencies are installed
pip list | grep flask

# Install missing dependencies
pip install flask flask-cors reportlab

# Check port availability
lsof -i :5000
```

### YouTube API Issues

Still applies from v1:
- Check `credentials.json` exists
- Delete `token.pickle` and re-authenticate
- Verify YouTube Analytics API is enabled

### No Data in Reports

- YouTube Analytics has 24-72 hour delay for Shorts
- Check date ranges are in the past
- Verify correct channel is authenticated

### Import Errors

```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## 📚 Documentation

- **Web Dashboard:** http://localhost:5000
- **API Docs:** http://localhost:5000/api/health
- **YETi Name:** YouTube Experiment Testing intelligence 👹
- **Quick Start:** See QUICKSTART_V2.md

## 🤝 Migration from v1

Good news: **No migration needed!** v2.0 is fully backward compatible.

Your existing:
- ✅ `experiments.yaml` works as-is
- ✅ CLI commands unchanged
- ✅ Markdown workflow still supported
- ✅ All v1 features available

New features are additive and optional.

## 📝 What's Next (Roadmap)

Coming in future versions:
- [ ] Multi-user authentication
- [ ] Real-time metrics streaming
- [ ] Automated variant rotation
- [ ] Machine learning predictions
- [ ] Integration with other platforms
- [ ] Mobile-responsive dashboard improvements
- [ ] Custom metric definitions
- [ ] Automated email reports

## 💡 Tips & Best Practices

1. **Sample Size**
   - Use the sample size calculator before running experiments
   - Aim for at least 1000 impressions per variant
   - More samples = more reliable results

2. **Statistical Significance**
   - Don't stop early just because you see a lift
   - Wait for statistical significance (p < 0.05)
   - Consider practical significance too (is the lift worth it?)

3. **Experiment Duration**
   - Run for at least 7 days to account for day-of-week effects
   - 14 days is better for seasonal patterns
   - Longer is generally better for reliability

4. **Variant Design**
   - Change one thing at a time for clear results
   - Test meaningful differences (small changes may not be detectable)
   - Document your variants clearly

5. **Metrics**
   - Choose metrics that align with your goals
   - Use CTR for thumbnails/titles
   - Use watch time for content quality
   - Track multiple metrics but have one primary goal

## 🙏 Credits

Built with:
- Flask - Web framework
- YouTube Analytics API - Data source
- ReportLab - PDF generation
- Matplotlib - Visualizations
- SciPy - Statistical analysis

## 📄 License

Same as v1 - check with repository owner.

---

**Version:** 2.0.0  
**Updated:** October 2025  
**Status:** MVP Complete



