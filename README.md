# 👹 YETi — YouTube Experiment Testing Intelligence

Stop guessing which thumbnail works. Run a proper A/B test.

I built YETi while growing a YouTube channel on Japanese real estate investment. Thumbnails and titles are the lever — but there was no tool that told me when a result was statistically significant vs. just noise. So I built one.

---

## What it does

- Runs A/B tests on thumbnails, titles, descriptions, and upload times
- Pulls real data from the YouTube Analytics API
- Calculates p-values, confidence intervals, and effect sizes
- Flags winners when the result is meaningful — not just lucky
- Generates PDF reports and CSV exports

Optional: pipe results through an OpenAI model for plain-English recommendations.

---

## Quick start

```bash
git clone https://github.com/calmannix/YETi.git
cd YETi
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp config_template.env .env  # Add your OpenAI key
```

Set up YouTube API credentials: [YOUTUBE_API_SETUP.md](YOUTUBE_API_SETUP.md)

```bash
python start_server.py
```

Open `http://localhost:5000`.

### CLI

```bash
python cli.py create --id exp_001 --name "Thumbnail test" \
  --start-date 2025-11-01 --end-date 2025-11-15 \
  --hypothesis "Red thumbnails increase CTR by 20%"

python cli.py analyse exp_001
python cli.py export exp_001 --format pdf
```

---

## Statistical methods

- Welch's t-test for continuous metrics (watch time, view duration)
- Z-test for rate metrics (CTR, conversion)
- 95% confidence intervals by default
- Cohen's d and Cohen's h for effect size
- Sample size calculator built in

---

## Stack

Python · Flask · YouTube Analytics API · SciPy · OpenAI API · ReportLab

---

Built for creators who want data, not vibes. [Issues welcome.](https://github.com/calmannix/YETi/issues)
