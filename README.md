# 👹 YETi - YouTube Experiment Testing Intelligence

A comprehensive A/B testing and analytics tool for YouTube content creators. Test thumbnails, titles, upload times, and more with statistical significance testing, AI-powered insights, and beautiful visualizations.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

### 🎯 Core Functionality
- **A/B Testing** - Test thumbnails, titles, descriptions, and more
- **Statistical Analysis** - Know if your results are meaningful (p-values, effect sizes, confidence intervals)
- **AI Insights** - Get intelligent recommendations powered by OpenAI
- **Video Variant Management** - Track different versions of your content
- **Real-time Monitoring** - Track experiment progress live

### 📊 Analytics & Reporting
- **Statistical Significance Testing** - T-tests, Z-tests for proportions
- **Sample Size Calculator** - Know how much data you need
- **Confidence Intervals** - Understand the range of likely outcomes
- **Power Analysis** - Ensure your experiments can detect real effects

### 🖥️ Multiple Interfaces
- **Web Dashboard** - Modern UI for managing experiments
- **REST API** - Programmatic access to all features
- **CLI** - Command-line interface for automation
- **Export Options** - PDF reports with charts, CSV data exports

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Google Cloud Project with YouTube Analytics API enabled
- OpenAI API key (for AI insights feature)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/calmannix/YETi.git
   cd YETi
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API credentials**
   
   a. **YouTube Analytics API Setup:**
   - Follow the guide in [YOUTUBE_API_SETUP.md](YOUTUBE_API_SETUP.md)
   - Download your `credentials.json` file
   - Place it in the project root directory
   
   b. **OpenAI API Setup (for AI insights):**
   - Copy the config template: `cp config_template.env .env`
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your-openai-api-key-here
     OPENAI_MODEL=gpt-4o-mini
     ```
   - Get your API key from: https://platform.openai.com/api-keys

5. **Verify setup**
   ```bash
   python verify_setup.py
   ```

6. **Start using YETi!**
   ```bash
   # Start web dashboard
   python start_server.py
   
   # Or use CLI
   python cli.py list
   ```

## 🚀 Usage

### Option 1: Web Dashboard (Recommended)

1. **Start the server:**
   ```bash
   python start_server.py
   ```

2. **Open your browser** to http://localhost:5000

3. **Features:**
   - Create and manage experiments
   - View real-time analytics
   - Run statistical analyses with one click
   - Generate and download reports
   - Get AI-powered insights

### Option 2: Command Line Interface

```bash
# List all experiments
python cli.py list

# Create a new experiment
python cli.py create --id exp_001 --name "Thumbnail Test" \
  --start-date 2025-11-01 --end-date 2025-11-15 \
  --hypothesis "Red thumbnails increase CTR by 20%"

# Analyze an experiment
python cli.py analyse exp_001

# Get AI insights
python cli.py insights exp_001

# Export results
python cli.py export exp_001 --format pdf
```

### Option 3: REST API

```python
import requests

# Get all experiments
response = requests.get('http://localhost:5000/api/experiments')
experiments = response.json()

# Analyze an experiment
response = requests.post('http://localhost:5000/api/experiments/exp_001/analyze')
analysis = response.json()

# Get AI insights
response = requests.post('http://localhost:5000/api/experiments/exp_001/insights')
insights = response.json()
```

## 📖 Quick Example

```python
from models.experiment_enhanced import EnhancedExperiment
from models.variant import VideoVariant, VariantType
from experiment_analyser import ExperimentAnalyser
from youtube_analytics import YouTubeAnalytics

# 1. Create experiment
exp = EnhancedExperiment(
    id="thumb_test_001",
    name="Thumbnail A/B Test",
    hypothesis="Bold thumbnails increase CTR by 15%",
    start_date="2025-11-01",
    end_date="2025-11-15",
    metrics={'primary': 'impressionClickThroughRate'},
    sample_size_target=5000,
    confidence_level=0.95
)

# 2. Add variants
variant_a = VideoVariant(
    id="control",
    variant_type=VariantType.THUMBNAIL,
    name="Original Thumbnail",
    is_control=True,
    video_ids=["VIDEO_ID_1", "VIDEO_ID_2"]
)

variant_b = VideoVariant(
    id="treatment",
    variant_type=VariantType.THUMBNAIL,
    name="Bold Red Thumbnail",
    video_ids=["VIDEO_ID_3", "VIDEO_ID_4"]
)

exp.add_variant(variant_a)
exp.add_variant(variant_b)

# 3. Run analysis
youtube = YouTubeAnalytics()
analyser = ExperimentAnalyser(youtube)
analysis = analyser.analyse_experiment(exp)

# 4. Check results
if analysis['statistical_significance']['is_significant']:
    print(f"✓ Significant! P-value: {analysis['statistical_significance']['p_value']:.4f}")
    print(f"Winner: {analysis['recommendation']['winner']}")
else:
    print("No significant difference found. Need more data.")
```

## 📊 Statistical Methods

YETi uses industry-standard statistical methods:

- **Two-Sample T-Test (Welch's)** - For continuous metrics (view duration, watch time)
- **Z-Test for Proportions** - For rate metrics (CTR, conversion rates)
- **Confidence Intervals** - 95% confidence by default (configurable)
- **Effect Size Calculations** - Cohen's d and Cohen's h
- **Power Analysis** - Ensure adequate sample sizes

### Interpreting Results

**P-value:**
- < 0.05: Statistically significant (95% confidence)
- < 0.01: Highly significant (99% confidence)
- ≥ 0.05: Not significant (could be due to chance)

**Effect Size:**
- < 0.2: Small effect
- 0.2 - 0.5: Medium effect
- > 0.5: Large effect

**Statistical Power:**
- > 0.80: Good (80% chance of detecting real effects)
- < 0.80: Need more samples

## 🤖 AI Insights

YETi includes an AI-powered insights agent that analyzes your experiment results and provides:

- **Actionable recommendations** based on statistical analysis
- **Pattern detection** across multiple experiments
- **Content optimization suggestions** for thumbnails, titles, and more
- **Anomaly detection** to identify unusual patterns
- **Future predictions** based on historical data

Enable AI insights by configuring your OpenAI API key in the `.env` file.

## 🌐 API Reference

### Experiments
```http
GET    /api/experiments              # List all experiments
POST   /api/experiments              # Create experiment
GET    /api/experiments/:id          # Get experiment details
PUT    /api/experiments/:id          # Update experiment
DELETE /api/experiments/:id          # Delete experiment
POST   /api/experiments/:id/analyze  # Run analysis
POST   /api/experiments/:id/insights # Get AI insights
POST   /api/experiments/:id/export   # Export results
```

### Dashboard
```http
GET    /api/dashboard/summary        # Get dashboard stats
```

### Statistics
```http
POST   /api/statistics/significance  # Calculate significance
POST   /api/statistics/sample-size   # Calculate sample size
```

See the full API documentation at http://localhost:5000/api/health

## 📁 Project Structure

```
YETi/
├── api/                    # Web server and REST API
├── models/                 # Data models (experiments, variants)
├── tests/                  # Unit tests
├── exports/                # Generated reports and exports
├── cli.py                  # Command-line interface
├── experiment_analyser.py  # Statistical analysis engine
├── insights_agent.py       # AI insights powered by OpenAI
├── youtube_analytics.py    # YouTube API integration
├── statistics_engine.py    # Statistical methods
├── export_manager.py       # Report generation
├── experiments.yaml        # Experiment storage
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```bash
# OpenAI API (required for AI insights)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Optional: Insights cache duration (seconds)
INSIGHTS_CACHE_DURATION=3600

# Optional: Server configuration
PORT=5000
DEBUG=False
```

### Files

- `credentials.json` - YouTube API credentials (download from Google Cloud Console)
- `token.pickle` - OAuth token (auto-generated on first run)
- `experiments.yaml` - Experiment data (auto-created)
- `.env` - API keys and configuration (create from `config_template.env`)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python run_tests.py

# Run specific test file
python -m pytest tests/test_statistics_engine.py

# Run with coverage
python -m pytest --cov=. tests/
```

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART_V2.md)** - Get up and running in 5 minutes
- **[YouTube API Setup](YOUTUBE_API_SETUP.md)** - Detailed setup instructions
- **[Setup FAQ](SETUP_FAQ.md)** - Common questions and troubleshooting
- **[API Documentation](api/)** - REST API reference

## 💡 Best Practices

1. **Sample Size** - Use the sample size calculator before running experiments
2. **Duration** - Run experiments for at least 7-14 days
3. **One Change at a Time** - Test one variable per experiment
4. **Statistical Significance** - Wait for p < 0.05 before declaring winners
5. **Multiple Metrics** - Track secondary metrics but have one primary goal

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [YouTube Analytics API](https://developers.google.com/youtube/analytics) - Data source
- [OpenAI API](https://openai.com/) - AI-powered insights
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [SciPy](https://scipy.org/) - Statistical analysis
- [Matplotlib](https://matplotlib.org/) - Data visualizations
- [ReportLab](https://www.reportlab.com/) - PDF generation

## 📧 Support

- **Issues**: Please report bugs via [GitHub Issues](https://github.com/calmannix/YETi/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/calmannix/YETi/discussions)

## 🗺️ Roadmap

- [ ] Multi-user authentication
- [ ] Real-time metrics streaming
- [ ] Automated variant rotation
- [ ] Machine learning predictions
- [ ] Integration with other platforms (TikTok, Instagram)
- [ ] Mobile app
- [ ] Custom metric definitions
- [ ] Automated email reports

---

**Version:** 2.1.0  
**Last Updated:** November 2025  
**Author:** [calmannix](https://github.com/calmannix)

Made with ❤️ for YouTube creators who love data

# YETi
