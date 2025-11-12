# Analytics Query Feature - Implementation Summary

## Overview

A natural language query interface has been added to YETi, allowing users to ask questions about their YouTube Analytics data in plain English. The system uses OpenAI's LLM to interpret questions and execute appropriate YouTube API calls.

**Date Implemented:** November 10, 2025  
**Difficulty Rating:** Medium (6/10)  
**Implementation Time:** ~6 hours

---

## What Was Built

### 1. Query Agent (`query_agent.py`)
- **Lines of Code:** ~400 lines
- **Purpose:** Parse natural language queries and execute YouTube API calls
- **Key Features:**
  - OpenAI function calling for query interpretation
  - Automatic date parsing ("last 3 months" → actual dates)
  - Support for video performance and aggregate statistics queries
  - LLM-powered response formatting
  - Comprehensive error handling

### 2. API Endpoint (`api/server.py`)
- **Endpoint:** `POST /api/query`
- **Request Format:**
  ```json
  {
    "question": "Which video had the most views in the last 3 months?"
  }
  ```
- **Response Format:**
  ```json
  {
    "success": true,
    "formatted": "Human-readable answer...",
    "data": { /* raw API data */ },
    "query_info": { /* parsed query details */ }
  }
  ```

### 3. Web UI (`api/templates/index.html`)
- **Section:** "💬 Ask Analytics"
- **Features:**
  - Clean chat interface with input field
  - Example questions for easy testing
  - Real-time query processing with loading indicators
  - Conversation history (session-scoped)
  - Responsive design matching existing dashboard

---

## How It Works

### Architecture Flow

```
User Question
    ↓
OpenAI Function Calling (parse intent + dates)
    ↓
YouTube Analytics API (fetch data)
    ↓
OpenAI Formatting (make it readable)
    ↓
Display to User
```

### Supported Query Types

1. **Video Performance Queries**
   - "Which video had the most views in the last 3 months?"
   - "Show me my top 5 videos by subscriber gain"
   - "What are my best performing videos this year?"

2. **Aggregate Statistics Queries**
   - "How many total views did I get last month?"
   - "Show me channel stats for this year"
   - "How many likes did I get last week?"

### Date Parsing Examples

| User Input | Parsed Date Range |
|------------|------------------|
| "last 3 months" | 90 days ago → today |
| "last month" | 30 days ago → today |
| "last week" | 7 days ago → today |
| "this year" | Jan 1 → today |
| "last year" | Jan 1 → Dec 31 (previous year) |

---

## Usage

### Via Web UI

1. Start the server:
   ```bash
   python start_server.py
   ```

2. Open browser to: `http://localhost:5000`

3. Scroll to "💬 Ask Analytics" section

4. Type your question or click an example

5. Press Enter or click "Ask"

### Via API

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Which video had the most views in the last month?"}'
```

### Python Code

```python
from query_agent import QueryAgent
from youtube_analytics import YouTubeAnalytics

# Initialize
youtube_api = YouTubeAnalytics()
query_agent = QueryAgent(youtube_api)

# Ask a question
result = query_agent.process_query(
    "Which video had the most views in the last 3 months?"
)

if result['success']:
    print(result['formatted'])
else:
    print(f"Error: {result['error']}")
```

---

## Testing

### Manual Testing

Run the test script:
```bash
python test_query_agent.py
```

This will:
1. Check credentials and API keys
2. Test the query agent with a sample question
3. Provide instructions for testing the API endpoint

### Sample Test Queries

Try these questions in the UI:
- "Which video had the most views in the last 3 months?"
- "Show me total channel views for this year"
- "What are my top 5 videos by subscriber gain?"
- "How many likes did I get last week?"
- "Show me videos from the last month"

---

## Technical Details

### OpenAI Function Calling

The agent uses two defined functions:

1. **get_video_performance**
   - Parameters: start_date, end_date, metrics, sort_by, limit
   - Use: Individual video queries

2. **get_aggregate_stats**
   - Parameters: start_date, end_date, metrics
   - Use: Channel-wide statistics

### YouTube Metrics Available

- views
- likes, comments, shares
- subscribersGained, subscribersLost
- estimatedMinutesWatched
- averageViewDuration, averageViewPercentage
- impressions, impressionClickThroughRate

### Error Handling

The system handles:
- Invalid queries (LLM explains why)
- API quota limits (graceful error messages)
- Date parsing failures (asks for clarification)
- No data found (informs user clearly)
- Missing API keys (setup instructions)

---

## Files Created

1. `query_agent.py` - Query processing logic (400 lines)
2. `test_query_agent.py` - Test suite (150 lines)
3. `ANALYTICS_QUERY_FEATURE.md` - This documentation

## Files Modified

1. `api/server.py` - Added `/api/query` endpoint (~40 lines)
2. `api/templates/index.html` - Added UI section (~270 lines total: CSS + HTML + JS)

---

## Requirements

### Already Met
- ✅ OpenAI API key in `.env` file
- ✅ YouTube Analytics API credentials
- ✅ Flask server running
- ✅ All dependencies in `requirements.txt`

### No New Dependencies
The feature uses existing packages:
- `openai` - Already installed
- `youtube_analytics` - Already implemented
- `flask` - Already installed

---

## Design Decisions

### Why This Approach?

1. **Simple Architecture**
   - No vector database needed
   - Direct API calls (fresh data)
   - Stateless (each query independent)

2. **User-Friendly**
   - Natural language (no API knowledge needed)
   - Example queries provided
   - Clear error messages

3. **Maintainable**
   - Single responsibility per component
   - Comprehensive error handling
   - Consistent with existing codebase

### What We Didn't Build

As per requirements, we kept it simple:
- ❌ No RAG/vector database
- ❌ No persistent conversation history
- ❌ No multi-turn context
- ❌ No query caching (always fresh data)

---

## Future Enhancements

If needed later, could add:
1. Query history storage (database)
2. Multi-turn conversations (context memory)
3. Query result caching (reduce API calls)
4. More complex queries (comparisons, trends)
5. Export query results (CSV/PDF)
6. Scheduled queries (alerts/reports)

---

## Success Criteria ✓

All criteria met:
- ✅ Users can ask natural language questions
- ✅ System correctly interprets date ranges
- ✅ YouTube API calls execute successfully
- ✅ Results display in readable format
- ✅ UI integrates seamlessly with dashboard

---

## Support

### Common Issues

**Q: "Query service not configured" error**  
A: Add `OPENAI_API_KEY` to your `.env` file

**Q: YouTube API errors**  
A: Check that `credentials.json` and `token.pickle` are set up correctly

**Q: No data returned**  
A: Verify you have videos in the specified date range

### Getting Help

1. Check test script output: `python test_query_agent.py`
2. Review API health: `http://localhost:5000/api/health`
3. Check browser console for JavaScript errors

---

**Implementation Complete** ✅  
**Difficulty:** Medium (6/10)  
**Status:** Production Ready

