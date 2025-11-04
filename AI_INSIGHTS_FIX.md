# AI Insights Dashboard View Fix

## Problem
The AI-powered insights section was displaying raw JSON from ChatGPT instead of the structured dashboard view with cards for proven practices, publishing specs, etc.

## Root Causes

1. **JSON Parsing Issue**: The insights agent was failing to parse JSON when ChatGPT returned it wrapped in markdown code blocks (```json...```)
2. **Narrative Fallback**: When parsing failed, the system fell back to displaying raw text/JSON in a "narrative" field
3. **Field Name Mismatches**: The HTML dashboard was looking for different field names than what the AI prompt was requesting

## Fixes Applied

### 1. Improved JSON Parsing (`insights_agent.py`)
- Added logic to strip markdown code blocks (```json...```) before parsing
- Better error handling with debug information
- Returns structured error messages instead of raw narrative text

### 2. Fixed Field Name Mismatches (`api/templates/index.html`)
Updated the dashboard to match the JSON structure from the AI prompt:

| Old Field Name | New Field Name | Description |
|---|---|---|
| `proven_best_practices` | `proven_practices` | List of proven strategies with data |
| `publishing_specifications` | `publishing_spec` | Publishing guidelines |
| `avoid_practices` | `failed_practices` | What didn't work |
| `proposed_next_experiments` | `next_experiments` | Suggested experiments |

### 3. Enhanced Dashboard Display
- **Impact Ranking**: Now shows top 5 winners with metrics (baseline → result)
- **Proven Practices**: Displays detailed specs with confidence levels and sample sizes
- **Publishing Spec**: Hierarchical display of all publishing parameters (title, hashtags, thumbnail, posting, video)
- **Failed Practices**: Shows what to avoid with reasons and sample sizes
- **Conflicts**: New section for conflicting results with recommendations
- **Next Experiments**: Shows proposed experiments with test design, rationale, and success metrics
- **Key Insight**: Prominently displays the main takeaway

### 4. Better Error Handling
- Clear error messages when JSON parsing fails
- Collapsible debug section showing raw response
- Helpful guidance for users

## JSON Structure Expected

The AI now returns this structured JSON:

```json
{
  "proven_practices": [
    {
      "element": "Title length",
      "specification": "38-42 characters",
      "baseline_metric": "127 subs per video",
      "test_metric": "423 subs per video",
      "absolute_change": 296,
      "percent_change": 233,
      "experiment_ids": ["exp_001"],
      "sample_size": 10,
      "confidence": "high",
      "notes": "..."
    }
  ],
  "publishing_spec": {
    "title": { ... },
    "hashtags": { ... },
    "thumbnail": { ... },
    "posting": { ... },
    "video": { ... }
  },
  "impact_ranking": [ ... ],
  "failed_practices": [ ... ],
  "conflicts": [ ... ],
  "next_experiments": [ ... ],
  "key_insight": "..."
}
```

## Testing

After making these changes, the AI insights should now display as a proper dashboard with:
- ✅ Colored cards for different insight types
- ✅ Visual hierarchy with grid layout
- ✅ Actionable data with exact specifications
- ✅ Confidence indicators
- ✅ "Create Experiment" buttons for suggestions
- ❌ No more raw JSON dumps

## What to Do If You Still See Raw JSON

1. Click "🔄 Refresh Insights" button to regenerate
2. If the error persists, check the debug section (expandable)
3. The raw response will show what ChatGPT actually returned
4. Most likely the AI needs another attempt to return valid JSON

## Files Modified

1. `path/to/YETi/insights_agent.py`
   - Enhanced `_call_openai()` method with markdown stripping
   - Better error handling and debug output

2. `path/to/YETi/api/templates/index.html`
   - Updated `displayAIInsights()` function
   - Fixed all field name mismatches
   - Enhanced visual display of all insight sections
   - Added new sections (conflicts, better next experiments)

