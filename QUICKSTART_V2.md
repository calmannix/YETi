# 👹 YETi Quick Start Guide - v2.0

Get up and running with YETi (YouTube Experiment Testing intelligence) in 5 minutes!

## 🚀 1-Minute Setup

```bash
# Navigate to project
cd path/to/YETi

# Activate virtual environment
source venv/bin/activate

# Install new dependencies (one-time)
pip install -r requirements.txt

# Start the server
python start_server.py
```

✨ **That's it!** Your browser will open automatically to the dashboard.

## 📊 Using the Dashboard

### View Your Experiments
The dashboard shows all your experiments at `http://localhost:5000`

**What you'll see:**
- 📈 Total experiments count
- ▶️ Active experiments
- ✅ Success rate
- 🔔 Experiments ready to analyze

### Quick Actions

**Start an Experiment:**
1. Find experiment with "DRAFT" status
2. Click "▶ Start" button
3. Confirm

**Analyze Results:**
1. Find experiment (active or completed)
2. Click "📊 Analyze" button
3. Wait for analysis to complete
4. Results appear automatically

**View Report:**
1. After analyzing, click "📄 View Report"
2. Report opens in modal window
3. Copy text or take screenshot

**Export Results:**
Use the API or wait for UI export button (coming soon)

## 🎯 Your First A/B Test

### Step 1: Create Experiment (CLI)
```bash
python cli.py create \
  --id thumb_test_001 \
  --name "Thumbnail A/B Test" \
  --hypothesis "Red thumbnails increase CTR by 15%" \
  --start-date 2025-10-22 \
  --end-date 2025-11-05 \
  --primary-metric impressionClickThroughRate \
  --success-metric impressionClickThroughRate \
  --success-threshold 15 \
  --success-operator increase \
  --treatment-videos "VIDEO_ID_1,VIDEO_ID_2" \
  --control-videos "VIDEO_ID_3,VIDEO_ID_4"
```

### Step 2: Start Experiment (Dashboard)
1. Open `http://localhost:5000`
2. Find "Thumbnail A/B Test"
3. Click "▶ Start"

### Step 3: Upload Your Videos
- Upload videos VIDEO_ID_1, VIDEO_ID_2 with red thumbnails
- Upload videos VIDEO_ID_3, VIDEO_ID_4 with original thumbnails

### Step 4: Wait for Data
Wait until Nov 5 (or date range completes)

### Step 5: Analyze (Dashboard)
1. Click "📊 Analyze" on your experiment
2. System fetches YouTube data
3. Calculates statistics
4. Shows success/failure

### Step 6: View Results
Click "📄 View Report" to see:
- Was it statistically significant?
- What was the P-value?
- Did you hit your goal?
- Detailed metrics comparison

## 📈 Statistical Significance Explained

Every analysis now tells you if results are **real or just random chance**.

**Look for these indicators:**

```
✓ Statistically significant (p=0.023)
Effect size: 0.45 (medium)
```

**What it means:**
- ✅ p < 0.05 = Results are reliable (not random)
- ✅ Effect size = How big the difference is
- ✅ Medium/Large effect = Worth implementing

**If you see:**
```
✗ No statistical significance (p=0.156)
```
- Need more data, or
- Change isn't big enough to detect, or
- Change doesn't exist

## 💡 Quick Tips

### Before Running Experiment

**Calculate Sample Size:**
```python
from statistics_engine import StatisticsEngine

engine = StatisticsEngine()
needed = engine.calculate_minimum_sample_size(
    baseline_rate=0.05,  # Current 5% CTR
    expected_lift=0.15,  # Expect 15% improvement
    power=0.80
)

print(f"Need {needed} impressions per variant")
# Might say: "Need 2,634 impressions per variant"
```

Run experiment long enough to get that many impressions!

### During Experiment

**DON'T:**
- ❌ Stop early just because you see a lift
- ❌ Keep running forever hoping for significance
- ❌ Change variants mid-experiment

**DO:**
- ✅ Wait for planned duration
- ✅ Check progress in dashboard
- ✅ Let it run 7-14 days minimum

### After Experiment

**If Significant (p < 0.05):**
- ✅ Implement the winning variant
- ✅ Document what worked
- ✅ Plan next test

**If Not Significant:**
- Try larger difference next time
- Run longer for more data
- Try different metric

## 🎨 Export Your Results

### PDF Report (Code)
```python
from export_manager import ExportManager
from experiment_manager import ExperimentManager

manager = ExperimentManager()
exp = manager.get_experiment("thumb_test_001")

if exp.results:
    exporter = ExportManager()
    pdf = exporter.export_to_pdf(exp.results, include_charts=True)
    print(f"Report saved: {pdf}")
```

### CSV Export (Code)
```python
csv = exporter.export_to_csv(exp.results)
# Open in Excel or Google Sheets
```

### Via API
```bash
curl -X POST http://localhost:5000/api/experiments/thumb_test_001/export \
  -H "Content-Type: application/json" \
  -d '{"format":"pdf"}' \
  --output report.pdf
```

## 🔧 Common Tasks

### View All Experiments
```bash
# CLI
python cli.py list

# Or open dashboard: http://localhost:5000
```

### Stop Running Experiment
```bash
# CLI
python cli.py stop thumb_test_001 --complete

# Or click "⏹ Stop" in dashboard
```

### Delete Experiment
```bash
# CLI  
python cli.py delete thumb_test_001

# Or click "🗑 Delete" in dashboard (confirms first)
```

### Check API Status
Visit: `http://localhost:5000/api/health`

Should see:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T...",
  "version": "2.0.0"
}
```

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check dependencies
pip list | grep flask

# Reinstall if needed
pip install flask flask-cors

# Try again
python start_server.py
```

### Dashboard Shows "API Offline"
1. Check server is running (look for console output)
2. Try refreshing page
3. Check `http://localhost:5000/api/health` directly

### "No experiments found"
- Check you're in the right directory
- Look for `experiments.yaml` file
- Try creating one: `python cli.py create ...`

### YouTube API Errors
- Delete `token.pickle`
- Run any command to re-authenticate
- Make sure `credentials.json` exists

## 📚 Next Steps

Now that you have the basics:

1. **Read the full docs:** `README_v2.md`
2. **Learn statistics:** Understand p-values and effect sizes
3. **Try variants:** Use the new variant system
4. **Automate:** Use the REST API
5. **Export:** Generate PDF reports for stakeholders

## 🎓 Best Practices

1. **One change at a time**
   - Test thumbnails OR titles, not both
   - Makes results clear

2. **Run long enough**
   - Minimum 7 days
   - Get enough impressions (use calculator)

3. **Set realistic goals**
   - 10-20% improvements are good
   - Bigger changes easier to detect

4. **Trust the statistics**
   - Don't stop early
   - Wait for p < 0.05
   - Consider effect size too

5. **Document everything**
   - What you tested
   - Why you tested it
   - What you learned

## ⌨️ Keyboard Shortcuts

Dashboard:
- `Ctrl+R` or `Cmd+R` - Refresh page
- `Ctrl+C` in terminal - Stop server

## 📞 Getting Help

1. **Check guides:**
   - `README_v2.md` - Full documentation
   - `UPGRADE_GUIDE.md` - Upgrade help
   - `MVP_SUMMARY.md` - Technical details

2. **Test API:**
   ```bash
   curl http://localhost:5000/api/health
   ```

3. **Check logs:**
   - Look at terminal where server is running
   - Error messages show there

4. **Verify setup:**
   ```bash
   python -c "import flask, reportlab, scipy; print('OK')"
   ```

## 🎉 You're Ready!

You now know:
- ✅ How to start the server
- ✅ How to use the dashboard
- ✅ How to run an A/B test
- ✅ What statistical significance means
- ✅ How to export results
- ✅ Basic troubleshooting

**Go run some experiments!** 🚀

---

**Need more?** See `README_v2.md` for complete documentation.



