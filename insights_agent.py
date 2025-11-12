"""AI-powered insights agent for experiment analysis."""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

from experiment_manager import Experiment

# Load environment variables
load_dotenv()


class InsightsAgent:
    """Generate AI-powered insights from experiment results."""
    
    def __init__(self):
        """Initialize the insights agent with OpenAI client."""
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.cache = {}
        self.cache_duration = int(os.getenv('INSIGHTS_CACHE_DURATION', 3600))
        self.cache_file = self._get_cache_file_path()
    
    def generate_insights(self, experiments: List[Experiment], channel_info: Dict = None, force_refresh: bool = False) -> Dict:
        """
        Generate AI-powered insights from all experiments.
        
        Args:
            experiments: List of experiments with results
            channel_info: Optional channel information (name, niche, subscribers)
            force_refresh: If True, bypass cache and generate fresh insights
        
        Returns:
            Dictionary with AI-generated insights
        """
        cache_key = f"insights_{len(experiments)}_{self._get_latest_analysis_date(experiments)}"
        
        # Check file cache first (unless force refresh)
        if not force_refresh:
            file_cache = self._load_cached_insights_from_file()
            if file_cache and self._is_cache_valid(file_cache, cache_key):
                print("✓ Using cached insights from file (to save API costs)")
                return file_cache['insights']
            
            # Check in-memory cache
            if cache_key in self.cache:
                cached_time, cached_insights = self.cache[cache_key]
                if datetime.now() - cached_time < timedelta(seconds=self.cache_duration):
                    print("✓ Using in-memory cached insights (to save API costs)")
                    return cached_insights
        
        # Prepare data for AI
        experiment_data = self._prepare_experiment_data(experiments, channel_info)
        
        # Generate insights using OpenAI
        print("🤖 Generating AI insights from your experiments...")
        insights = self._call_openai(experiment_data)
        
        # Cache results in memory
        self.cache[cache_key] = (datetime.now(), insights)
        
        # Save to file cache
        self._save_insights_to_file(cache_key, insights, len(experiments))
        
        return insights
    
    def _prepare_experiment_data(self, experiments: List[Experiment], channel_info: Dict = None) -> Dict:
        """Prepare experiment data in format suitable for AI analysis."""
        analyzed_experiments = [e for e in experiments if e.results]
        
        experiments_list = []
        for exp in analyzed_experiments:
            exp_data = {
                'id': exp.id,
                'name': exp.name,
                'hypothesis': exp.hypothesis,
                'period': f"{exp.start_date} to {exp.end_date}",
                'success': exp.results.get('success', False),
                'metric': exp.metrics['primary']
            }
            
            # Get primary metric results
            primary_metric = exp.metrics['primary']
            if primary_metric in exp.results.get('metrics', {}):
                metric_data = exp.results['metrics'][primary_metric]
                
                if 'treatment_vs_control' in metric_data:
                    exp_data['impact_percent'] = metric_data['treatment_vs_control']['change_percent']
                    exp_data['treatment_value'] = metric_data.get('treatment_value')
                    exp_data['control_value'] = metric_data.get('control_value')
                elif metric_data.get('change_percent') is not None:
                    exp_data['impact_percent'] = metric_data['change_percent']
            
            experiments_list.append(exp_data)
        
        # Prepare summary
        successful = [e for e in experiments_list if e.get('success')]
        failed = [e for e in experiments_list if not e.get('success')]
        
        data = {
            'channel': channel_info or {},
            'experiments': experiments_list,
            'summary': {
                'total_experiments': len(experiments_list),
                'successful': len(successful),
                'failed': len(failed),
                'success_rate': (len(successful) / len(experiments_list) * 100) if experiments_list else 0,
                'analyzed_count': len(analyzed_experiments)
            }
        }
        
        return data
    
    def _call_openai(self, data: Dict) -> Dict:
        """Call OpenAI API to generate insights."""
        
        # Create prompt
        prompt = self._build_prompt(data)
        
        try:
            # Use JSON mode to ensure valid JSON response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert YouTube growth strategist and data analyst. You analyze A/B test results to provide actionable insights and recommendations. Be specific, data-driven, and practical. You MUST respond with valid JSON only - no markdown, no code blocks, just pure JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={"type": "json_object"},  # Force JSON output
                temperature=0.7,
                max_tokens=3000  # Increased for complete responses
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                # Clean up response if needed
                cleaned_response = ai_response.strip()
                
                # Remove markdown code blocks if somehow still present
                if cleaned_response.startswith('```'):
                    lines = cleaned_response.split('\n')
                    lines = lines[1:]  # Remove first line (```json or ```)
                    if lines and lines[-1].strip() == '```':
                        lines = lines[:-1]  # Remove last line (```)
                    cleaned_response = '\n'.join(lines)
                
                # Parse JSON
                insights = json.loads(cleaned_response)
                
            except json.JSONDecodeError as e:
                # Try to fix common JSON issues
                print(f"⚠️  Failed to parse AI response as JSON: {e}")
                print(f"Attempting to fix common JSON issues...")
                
                # Try to extract JSON if wrapped in other content
                import re
                json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                if json_match:
                    try:
                        insights = json.loads(json_match.group(0))
                        print("✓ Successfully extracted JSON from response")
                    except:
                        print(f"✗ Could not parse extracted JSON")
                        print(f"Response preview: {ai_response[:500]}...")
                        insights = {
                            'error': 'Failed to parse AI response',
                            'message': f'The AI returned invalid JSON. Please try again. Error: {str(e)}',
                            'raw_response': ai_response[:2000]  # More chars for debugging
                        }
                else:
                    print(f"Response preview: {ai_response[:500]}...")
                    insights = {
                        'error': 'Failed to parse AI response',
                        'message': f'The AI returned invalid JSON. Please try again. Error: {str(e)}',
                        'raw_response': ai_response[:2000]
                    }
            
            insights['generated_at'] = datetime.now().isoformat()
            insights['model'] = self.model
            
            return insights
            
        except Exception as e:
            return {
                'error': str(e),
                'message': 'Failed to generate insights. Check API key and connection.',
                'generated_at': datetime.now().isoformat()
            }
    
    def _build_prompt(self, data: Dict) -> str:
        """Build the prompt for OpenAI using improved format."""
        
        # Find best performing result
        best_result = None
        best_impact = 0
        for exp in data['experiments']:
            if exp.get('success') and exp.get('impact_percent', 0) > best_impact:
                best_impact = exp['impact_percent']
                best_result = f"{exp['name']} (+{best_impact:.1f}%)"
        
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        prompt = f"""You're an expert YouTube data analytics who specialises in analysing YouTube Shorts experiments to extract actionable publishing recommendations.

CONTEXT:

Current date: {current_date}

Total experiments: {data['summary']['total_experiments']}

Best result: {best_result or 'Not yet determined'}

Success rate: {data['summary']['success_rate']:.1f}%

EXPERIMENT DATA:
{json.dumps(data['experiments'], indent=2)}

TASK:

Analyse the experiment data above and provide specific, evidence-based recommendations. Structure your response as JSON (no markdown blocks).

1. IDENTIFY PATTERNS

Extract what definitively works and what failed. Note where results conflict.

2. SPECIFY MECHANICS

For each tested variable, provide exact specifications:

- Titles: character count range, structure, keyword placement

- Hashtags: count, types, position (caption vs title)

- Thumbnails: style elements, text overlay specs, composition

- Posting cadence: frequency and timing with timezone

- Video length: duration ranges if tested

- Other variables: specific parameters that moved metrics

3. QUANTIFY IMPACT

Rank recommendations by performance gain. Show baseline vs test metrics.

4. PROPOSE EXPERIMENTS

Suggest 5 untested variables. Requirements:

- Must not duplicate completed experiments

- Explain why each compounds existing gains

- Estimate impact range based on similar tests

- **Order by priority: HIGH priority experiments FIRST, then medium, then low**

JSON STRUCTURE:

{{
  "proven_practices": [
    {{
      "element": "string (e.g., 'Title length')",
      "specification": "string (exact parameters, e.g., '38-42 characters, front-load hook word, end with #hashtag')",
      "baseline_metric": "string (e.g., '127 subs per video')",
      "test_metric": "string (e.g., '423 subs per video')",
      "absolute_change": "number (296)",
      "percent_change": "number (233)",
      "experiment_ids": ["array of strings"],
      "sample_size": "number",
      "confidence": "high|medium|low",
      "notes": "string (conflicts, caveats, conditions)"
    }}
  ],
  "publishing_spec": {{
    "title": {{
      "length_chars": "string (e.g., '38-42')",
      "length_words": "string (e.g., '5-7')",
      "structure": "string (formula)",
      "keywords": "string (placement rules)",
      "hashtags_in_title": "string (count and position)"
    }},
    "hashtags": {{
      "total_count": "string",
      "placement": "string (title and/or caption)",
      "types": "string (niche/broad mix)",
      "examples": ["array of strings"]
    }},
    "thumbnail": {{
      "style": "string",
      "text_overlay": "string (yes/no, specs)",
      "key_elements": ["array of strings"],
      "avoid": ["array of strings"]
    }},
    "posting": {{
      "frequency": "string (per day/week)",
      "timing": "string (time and timezone if tested)",
      "gaps": "string (hours between posts)"
    }},
    "video": {{
      "length_seconds": "string (range if tested)",
      "hook_timing": "string (first X seconds)",
      "other_specs": "string"
    }}
  }},
  "failed_practices": [
    {{
      "practice": "string",
      "metric_impact": "string",
      "percent_loss": "number",
      "why_failed": "string (hypothesis)",
      "experiment_ids": ["array"],
      "sample_size": "number"
    }}
  ],
  "next_experiments": [
    {{
      "id": "string (sequential)",
      "variable": "string (what you'll test)",
      "hypothesis": "string (expected outcome with number)",
      "test_design": "string (A vs B specifics)",
      "expected_impact": "string (range)",
      "priority": "high|medium|low",
      "rationale": "string (why this compounds current wins)",
      "success_metric": "string (what measures success)"
    }}
  ],
  "conflicts": [
    {{
      "variable": "string",
      "conflicting_results": "string",
      "possible_reasons": ["array"],
      "recommendation": "string"
    }}
  ],
  "key_insight": "string (one sentence, most important finding)"
}}

RULES:

- Only state what data supports. Flag low confidence.

- Use exact numbers: "38-42 characters" not "short titles"

- Show absolute and percentage changes

- Note sample sizes under 5 as "early signal"

- If experiments conflict, include in "conflicts" array

- Proposed experiments must be genuinely new

- Return valid JSON only

CALCULATIONS:

For each proven practice, show:

- Baseline performance (control or previous average)

- Test performance

- Absolute difference

- Percentage change: ((test - baseline) / baseline) × 100

When data is thin, provide direction but mark confidence as low."""

        return prompt
    
    def _get_latest_analysis_date(self, experiments: List[Experiment]) -> str:
        """Get the most recent analysis date from experiments."""
        dates = [
            e.results.get('analysis_date', '')
            for e in experiments
            if e.results
        ]
        return max(dates) if dates else datetime.now().isoformat()
    
    def clear_cache(self):
        """Clear the insights cache."""
        self.cache = {}
        print("✓ Insights cache cleared")
    
    def _get_cache_file_path(self) -> Path:
        """Get the path to the cache file."""
        return Path(__file__).parent / 'insights_cache.json'
    
    def _load_cached_insights_from_file(self) -> Optional[Dict]:
        """
        Load cached insights from file.
        
        Returns:
            Cached insights dict or None if file doesn't exist or is invalid
        """
        try:
            if not self.cache_file.exists():
                return None
            
            with open(self.cache_file, 'r') as f:
                cached_data = json.load(f)
            
            return cached_data
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Warning: Could not load insights cache file: {e}")
            return None
    
    def _save_insights_to_file(self, cache_key: str, insights: Dict, experiment_count: int):
        """
        Save insights to file cache.
        
        Args:
            cache_key: The cache key for validation
            insights: The insights data to save
            experiment_count: Number of experiments analyzed
        """
        try:
            cache_data = {
                'cache_key': cache_key,
                'generated_at': datetime.now().isoformat(),
                'experiment_count': experiment_count,
                'insights': insights
            }
            
            with open(self.cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            
            print(f"✓ Insights cached to file: {self.cache_file}")
        except IOError as e:
            print(f"⚠️  Warning: Could not save insights cache file: {e}")
            # Continue with in-memory cache only
    
    def _is_cache_valid(self, cached_data: Dict, current_cache_key: str) -> bool:
        """
        Check if cached insights are still valid.
        
        Args:
            cached_data: The cached data from file
            current_cache_key: The current cache key to validate against
        
        Returns:
            True if cache is valid, False otherwise
        """
        try:
            # Check if cache key matches
            if cached_data.get('cache_key') != current_cache_key:
                print("⚠️  Cache invalid: experiment data changed")
                return False
            
            # Check if cache has expired
            generated_at = datetime.fromisoformat(cached_data.get('generated_at', ''))
            age = datetime.now() - generated_at
            
            if age > timedelta(seconds=self.cache_duration):
                print(f"⚠️  Cache expired (age: {age.total_seconds():.0f}s, limit: {self.cache_duration}s)")
                return False
            
            return True
        except (KeyError, ValueError) as e:
            print(f"⚠️  Cache validation failed: {e}")
            return False

