"""Time series analysis for YouTube experiment data."""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

try:
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.tsa.stattools import adfuller
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("Warning: statsmodels not available. Time series features will be limited. Install with: pip install statsmodels")


class TimeSeriesAnalyzer:
    """Analyze time series patterns in YouTube metrics."""
    
    def __init__(self):
        """Initialize time series analyzer."""
        self.statsmodels_available = STATSMODELS_AVAILABLE
    
    def detect_trends(
        self,
        dates: List[str],
        values: List[float],
        model: str = 'additive'
    ) -> Dict:
        """
        Detect trends and seasonality in time series data.
        
        Args:
            dates: List of date strings in YYYY-MM-DD format
            values: List of metric values
            model: 'additive' or 'multiplicative' decomposition model
        
        Returns:
            Dictionary with trend, seasonal, and residual components
        """
        if not STATSMODELS_AVAILABLE:
            return {
                'trend': None,
                'seasonal': None,
                'residual': None,
                'has_trend': False,
                'has_seasonality': False,
                'message': 'statsmodels not available'
            }
        
        if len(values) < 2:
            return {
                'trend': None,
                'seasonal': None,
                'residual': None,
                'has_trend': False,
                'has_seasonality': False,
                'message': 'Insufficient data'
            }
        
        try:
            # Convert to pandas Series with datetime index
            df = pd.DataFrame({
                'date': pd.to_datetime(dates),
                'value': values
            })
            df.set_index('date', inplace=True)
            
            # Ensure we have enough data points for decomposition
            min_periods = 7 if model == 'additive' else 14
            if len(df) < min_periods:
                # Simple linear trend detection
                return self._simple_trend_detection(df['value'])
            
            # Seasonal decomposition
            decomposition = seasonal_decompose(
                df['value'],
                model=model,
                period=min(7, len(df) // 2) if len(df) >= 7 else None,
                extrapolate_trend='freq'
            )
            
            trend = decomposition.trend.dropna().tolist()
            seasonal = decomposition.seasonal.dropna().tolist()
            residual = decomposition.resid.dropna().tolist()
            
            # Detect if there's a significant trend
            has_trend = self._has_significant_trend(trend)
            
            # Detect if there's seasonality
            has_seasonality = self._has_seasonality(seasonal)
            
            return {
                'trend': trend,
                'seasonal': seasonal,
                'residual': residual,
                'has_trend': has_trend,
                'has_seasonality': has_seasonality,
                'trend_direction': self._get_trend_direction(trend),
                'seasonal_strength': self._calculate_seasonal_strength(seasonal, values),
                'trend_strength': self._calculate_trend_strength(trend, values)
            }
        except Exception as e:
            return {
                'trend': None,
                'seasonal': None,
                'residual': None,
                'has_trend': False,
                'has_seasonality': False,
                'message': f'Error in decomposition: {str(e)}'
            }
    
    def _simple_trend_detection(self, values: pd.Series) -> Dict:
        """Simple linear trend detection for small datasets."""
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        has_trend = abs(slope) > np.std(values) * 0.1
        
        return {
            'trend': values.tolist(),
            'seasonal': [0] * len(values),
            'residual': [0] * len(values),
            'has_trend': has_trend,
            'has_seasonality': False,
            'trend_direction': 'increasing' if slope > 0 else 'decreasing',
            'trend_strength': abs(slope) / np.mean(values) if np.mean(values) > 0 else 0
        }
    
    def _has_significant_trend(self, trend: List[float]) -> bool:
        """Check if trend component is significant."""
        if not trend or len(trend) < 2:
            return False
        
        # Simple check: if first and last values differ significantly
        first_val = trend[0]
        last_val = trend[-1]
        
        if first_val == 0:
            return abs(last_val) > 0.1
        
        change_pct = abs((last_val - first_val) / first_val)
        return change_pct > 0.05  # 5% change threshold
    
    def _has_seasonality(self, seasonal: List[float]) -> bool:
        """Check if seasonal component is significant."""
        if not seasonal:
            return False
        
        # Check if seasonal variation is significant
        seasonal_std = np.std(seasonal)
        seasonal_mean = np.abs(np.mean(seasonal))
        
        # If standard deviation is significant relative to mean
        if seasonal_mean == 0:
            return seasonal_std > 0.1
        
        return (seasonal_std / seasonal_mean) > 0.1 if seasonal_mean > 0 else False
    
    def _get_trend_direction(self, trend: List[float]) -> str:
        """Get trend direction."""
        if not trend or len(trend) < 2:
            return 'none'
        
        first_val = trend[0]
        last_val = trend[-1]
        
        if first_val == 0:
            return 'increasing' if last_val > 0 else 'decreasing'
        
        change_pct = (last_val - first_val) / first_val
        
        if change_pct > 0.05:
            return 'increasing'
        elif change_pct < -0.05:
            return 'decreasing'
        else:
            return 'stable'
    
    def _calculate_seasonal_strength(self, seasonal: List[float], original: List[float]) -> float:
        """Calculate strength of seasonal component."""
        if not seasonal or not original:
            return 0.0
        
        try:
            var_seasonal = np.var(seasonal)
            var_original = np.var(original)
            
            if var_original == 0:
                return 0.0
            
            return min(var_seasonal / var_original, 1.0)
        except:
            return 0.0
    
    def _calculate_trend_strength(self, trend: List[float], original: List[float]) -> float:
        """Calculate strength of trend component."""
        if not trend or not original:
            return 0.0
        
        try:
            var_trend = np.var(trend)
            var_original = np.var(original)
            
            if var_original == 0:
                return 0.0
            
            return min(var_trend / var_original, 1.0)
        except:
            return 0.0
    
    def detect_weekly_patterns(
        self,
        dates: List[str],
        values: List[float]
    ) -> Dict:
        """
        Detect weekly patterns in the data.
        
        Args:
            dates: List of date strings
            values: List of metric values
        
        Returns:
            Dictionary with day-of-week analysis
        """
        try:
            df = pd.DataFrame({
                'date': pd.to_datetime(dates),
                'value': values
            })
            
            # Add day of week
            df['day_of_week'] = df['date'].dt.day_name()
            df['day_of_week_num'] = df['date'].dt.dayofweek
            
            # Group by day of week
            daily_stats = df.groupby('day_of_week').agg({
                'value': ['mean', 'std', 'count']
            }).round(2)
            
            # Calculate which day is best
            daily_means = df.groupby('day_of_week')['value'].mean()
            best_day = daily_means.idxmax()
            worst_day = daily_means.idxmin()
            
            # Detect if there's a significant weekly pattern
            day_std = daily_means.std()
            overall_mean = df['value'].mean()
            has_pattern = (day_std / overall_mean) > 0.1 if overall_mean > 0 else False
            
            return {
                'has_weekly_pattern': has_pattern,
                'best_day': best_day,
                'worst_day': worst_day,
                'daily_means': daily_means.to_dict(),
                'pattern_strength': min(day_std / overall_mean, 1.0) if overall_mean > 0 else 0.0,
                'daily_stats': daily_stats.to_dict()
            }
        except Exception as e:
            return {
                'has_weekly_pattern': False,
                'message': f'Error in weekly pattern detection: {str(e)}'
            }
    
    def adjust_for_trends(
        self,
        dates: List[str],
        values: List[float],
        control_dates: List[str],
        control_values: List[float]
    ) -> Tuple[List[float], List[float]]:
        """
        Adjust values for trends before comparison.
        
        This helps account for natural trends (like subscriber growth)
        when comparing experiment and control groups.
        
        Args:
            dates: Experiment dates
            values: Experiment values
            control_dates: Control dates
            control_values: Control values
        
        Returns:
            Tuple of (adjusted_experiment_values, adjusted_control_values)
        """
        if not STATSMODELS_AVAILABLE:
            return values, control_values
        
        try:
            # Detect trends in control group
            control_trend = self.detect_trends(control_dates, control_values)
            
            if not control_trend.get('has_trend'):
                return values, control_values
            
            # Simple linear detrending
            # For now, return original values
            # More sophisticated detrending can be added later
            return values, control_values
        except:
            return values, control_values
    
    def forecast_metric(
        self,
        dates: List[str],
        values: List[float],
        periods: int = 7
    ) -> Dict:
        """
        Forecast future metric values.
        
        Args:
            dates: Historical dates
            values: Historical values
            periods: Number of periods to forecast
        
        Returns:
            Dictionary with forecast and confidence intervals
        """
        if not STATSMODELS_AVAILABLE or len(values) < 7:
            # Simple linear forecast
            if len(values) < 2:
                return {'forecast': None, 'message': 'Insufficient data'}
            
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            
            future_x = np.arange(len(values), len(values) + periods)
            forecast = slope * future_x + intercept
            
            # Simple confidence interval (assuming normal distribution)
            residuals = values - (slope * x + intercept)
            std_err = np.std(residuals)
            
            return {
                'forecast': forecast.tolist(),
                'lower_bound': (forecast - 1.96 * std_err).tolist(),
                'upper_bound': (forecast + 1.96 * std_err).tolist(),
                'method': 'linear'
            }
        
        # More sophisticated forecasting can be added here
        # For now, use simple linear forecast
        return self.forecast_metric(dates, values, periods)

