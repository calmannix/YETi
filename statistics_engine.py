"""
Statistical analysis engine for A/B test experiments.

This module provides comprehensive statistical testing with multiple library support:
- Pingouin: Advanced statistical functions with robust error handling (preferred)
- SciPy: Core statistical computations
- Statsmodels: Specialized proportion tests
- Custom implementations: Fallback when libraries unavailable

Features:
- Two-sample t-tests (Welch's t-test)
- Z-tests for proportions
- Effect size calculations (Cohen's d, Cohen's h)
- Statistical power analysis
- Sample size calculations
- Comprehensive input validation
- Robust error handling for edge cases
"""

import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import numpy as np

try:
    from scipy import stats
    from scipy.stats import norm, t, ttest_ind, ttest_ind_from_stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("Warning: scipy not available. Using custom statistical functions. Install with: pip install scipy")

try:
    from statsmodels.stats.proportion import proportions_ztest
    from statsmodels.stats.weightstats import ttest_ind as ttest_ind_weighted
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("Warning: statsmodels not available. Using custom statistical functions. Install with: pip install statsmodels")

try:
    import pingouin as pg
    PINGOUIN_AVAILABLE = True
except ImportError:
    PINGOUIN_AVAILABLE = False
    print("Warning: pingouin not available. Using scipy/statsmodels for statistical functions. Install with: pip install pingouin")


@dataclass
class StatisticalResult:
    """Results of statistical significance testing."""
    is_significant: bool
    p_value: float
    confidence_level: float
    effect_size: float
    power: float
    sample_size_needed: int
    test_type: str
    conclusion: str


class StatisticsEngine:
    """
    Perform statistical analysis on experiment results.
    
    Supports:
    - Two-sample t-tests
    - Z-tests for proportions
    - Chi-square tests
    - Confidence intervals
    - Statistical power analysis
    """
    
    def __init__(self, confidence_level: float = 0.95):
        """
        Initialize statistics engine.
        
        Args:
            confidence_level: Desired confidence level (default 0.95 for 95%)
        """
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    # Input Validation Methods
    
    def _validate_sample_data(
        self,
        mean: float,
        std: float,
        size: int,
        param_name: str = "sample"
    ) -> None:
        """
        Validate sample data for t-tests.
        
        Args:
            mean: Sample mean
            std: Sample standard deviation
            size: Sample size
            param_name: Name of parameter for error messages
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if not isinstance(size, (int, np.integer)) or size <= 0:
            raise ValueError(f"{param_name}_size must be a positive integer, got {size}")
        
        if std < 0:
            raise ValueError(f"{param_name}_std must be non-negative, got {std}")
        
        if not math.isfinite(mean):
            raise ValueError(f"{param_name}_mean must be a finite number, got {mean}")
        
        if not math.isfinite(std):
            raise ValueError(f"{param_name}_std must be a finite number, got {std}")
    
    def _validate_proportion_data(
        self,
        successes: int,
        total: int,
        param_name: str = "sample"
    ) -> None:
        """
        Validate proportion data for z-tests.
        
        Args:
            successes: Number of successes
            total: Total observations
            param_name: Name of parameter for error messages
        
        Raises:
            ValueError: If any parameter is invalid
        """
        if not isinstance(total, (int, np.integer)) or total <= 0:
            raise ValueError(f"{param_name}_total must be a positive integer, got {total}")
        
        if not isinstance(successes, (int, np.integer)) or successes < 0:
            raise ValueError(f"{param_name}_successes must be a non-negative integer, got {successes}")
        
        if successes > total:
            raise ValueError(
                f"{param_name}_successes ({successes}) cannot exceed {param_name}_total ({total})"
            )
    
    def _validate_confidence_level(self, confidence_level: float) -> None:
        """
        Validate confidence level parameter.
        
        Args:
            confidence_level: Confidence level (e.g., 0.95 for 95%)
        
        Raises:
            ValueError: If confidence level is invalid
        """
        if not isinstance(confidence_level, (float, int)):
            raise ValueError(f"confidence_level must be a number, got {type(confidence_level)}")
        
        if not 0 < confidence_level < 1:
            raise ValueError(f"confidence_level must be between 0 and 1, got {confidence_level}")
    
    def _validate_rate(self, rate: float, param_name: str = "rate") -> None:
        """
        Validate rate/proportion parameter.
        
        Args:
            rate: Rate or proportion value
            param_name: Name of parameter for error messages
        
        Raises:
            ValueError: If rate is invalid
        """
        if not isinstance(rate, (float, int)):
            raise ValueError(f"{param_name} must be a number, got {type(rate)}")
        
        if not math.isfinite(rate):
            raise ValueError(f"{param_name} must be a finite number, got {rate}")
        
        if not 0 <= rate <= 1:
            raise ValueError(f"{param_name} must be between 0 and 1, got {rate}")
    
    def _validate_numeric(self, value: float, param_name: str, min_value: float = None) -> None:
        """
        Validate a numeric parameter.
        
        Args:
            value: Value to validate
            param_name: Name of parameter for error messages
            min_value: Optional minimum value
        
        Raises:
            ValueError: If value is invalid
        """
        if not isinstance(value, (float, int)):
            raise ValueError(f"{param_name} must be a number, got {type(value)}")
        
        if not math.isfinite(value):
            raise ValueError(f"{param_name} must be a finite number, got {value}")
        
        if min_value is not None and value < min_value:
            raise ValueError(f"{param_name} must be >= {min_value}, got {value}")
    
    def t_test_two_sample(
        self,
        sample1_mean: float,
        sample1_std: float,
        sample1_size: int,
        sample2_mean: float,
        sample2_std: float,
        sample2_size: int
    ) -> StatisticalResult:
        """
        Perform two-sample t-test (Welch's t-test).
        
        Used for comparing means of continuous metrics like average view duration.
        Uses Pingouin, scipy.stats, or custom calculations with comprehensive error handling.
        
        Raises:
            ValueError: If input parameters are invalid
        """
        # Validate inputs
        self._validate_sample_data(sample1_mean, sample1_std, sample1_size, "sample1")
        self._validate_sample_data(sample2_mean, sample2_std, sample2_size, "sample2")
        
        try:
            # Perform t-test using available libraries
            if SCIPY_AVAILABLE and sample1_size > 1 and sample2_size > 1:
                # Use scipy's ttest_ind_from_stats for accurate Welch's t-test
                # This handles unequal variances correctly
                t_stat, p_value = ttest_ind_from_stats(
                    mean1=sample1_mean,
                    std1=sample1_std,
                    nobs1=sample1_size,
                    mean2=sample2_mean,
                    std2=sample2_std,
                    nobs2=sample2_size,
                    equal_var=False  # Welch's t-test (unequal variances)
                )
                
                # Calculate degrees of freedom (Welch-Satterthwaite)
                df = self._calculate_welch_df(
                    sample1_std, sample1_size,
                    sample2_std, sample2_size
                )
                test_type = "Two-sample t-test (Welch's - scipy)"
            else:
                # Fallback to custom calculation
                se1 = (sample1_std ** 2) / sample1_size
                se2 = (sample2_std ** 2) / sample2_size
                se = math.sqrt(se1 + se2)
                
                t_stat = (sample1_mean - sample2_mean) / se if se > 0 else 0
                df = self._calculate_welch_df(
                    sample1_std, sample1_size,
                    sample2_std, sample2_size
                )
                p_value = self._t_to_p_value(abs(t_stat), df)
                test_type = "Two-sample t-test (Welch's)"
            
            # Effect size (Cohen's d)
            # Use Pingouin's compute_effsize if available for more accurate calculation
            if PINGOUIN_AVAILABLE:
                try:
                    # Pingouin's Cohen's d calculation
                    effect_size = pg.compute_effsize(
                        sample1_mean, sample2_mean,
                        sample1_std, sample2_std,
                        sample1_size, sample2_size,
                        eftype='cohen'
                    )
                    effect_size = abs(effect_size)
                except Exception:
                    # Fallback to manual calculation
                    pooled_std = math.sqrt(
                        ((sample1_size - 1) * sample1_std**2 + (sample2_size - 1) * sample2_std**2) /
                        (sample1_size + sample2_size - 2)
                    )
                    effect_size = abs(sample1_mean - sample2_mean) / pooled_std if pooled_std > 0 else 0
            else:
                # Manual Cohen's d calculation
                pooled_std = math.sqrt(
                    ((sample1_size - 1) * sample1_std**2 + (sample2_size - 1) * sample2_std**2) /
                    (sample1_size + sample2_size - 2)
                )
                effect_size = abs(sample1_mean - sample2_mean) / pooled_std if pooled_std > 0 else 0
            
            # Statistical power calculation
            # Use Pingouin's power_ttest if available
            if PINGOUIN_AVAILABLE and effect_size > 0:
                try:
                    power = pg.power_ttest(
                        d=effect_size,
                        n=min(sample1_size, sample2_size),
                        alpha=self.alpha,
                        alternative='two-sided'
                    )
                    power = max(0.0, min(1.0, power))  # Clamp to [0, 1]
                except Exception:
                    # Fallback to scipy or custom
                    if SCIPY_AVAILABLE:
                        power = self._calculate_power_scipy(effect_size, sample1_size, sample2_size)
                    else:
                        power = self._calculate_power(effect_size, sample1_size + sample2_size)
            elif SCIPY_AVAILABLE:
                power = self._calculate_power_scipy(effect_size, sample1_size, sample2_size)
            else:
                power = self._calculate_power(effect_size, sample1_size + sample2_size)
            
            # Sample size needed for 80% power
            if PINGOUIN_AVAILABLE and effect_size > 0:
                try:
                    needed = pg.power_ttest(
                        d=effect_size,
                        power=0.80,
                        alpha=self.alpha,
                        alternative='two-sided'
                    )
                    needed = max(int(math.ceil(needed)), 100)
                except Exception:
                    # Fallback to scipy or custom
                    if SCIPY_AVAILABLE:
                        needed = self._calculate_sample_size_needed_scipy(effect_size, 0.80, self.alpha)
                    else:
                        needed = self._calculate_sample_size_needed(effect_size, 0.80, self.alpha)
            elif SCIPY_AVAILABLE:
                needed = self._calculate_sample_size_needed_scipy(effect_size, 0.80, self.alpha)
            else:
                needed = self._calculate_sample_size_needed(effect_size, 0.80, self.alpha)
            
            is_significant = p_value < self.alpha
            
            conclusion = self._generate_conclusion(
                is_significant, p_value, effect_size,
                sample1_mean, sample2_mean, "mean"
            )
            
            return StatisticalResult(
                is_significant=is_significant,
                p_value=p_value,
                confidence_level=self.confidence_level,
                effect_size=effect_size,
                power=power,
                sample_size_needed=needed,
                test_type=test_type,
                conclusion=conclusion
            )
        
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise RuntimeError(f"Error performing t-test: {str(e)}") from e
    
    def z_test_proportions(
        self,
        successes1: int,
        total1: int,
        successes2: int,
        total2: int
    ) -> StatisticalResult:
        """
        Perform z-test for comparing two proportions.
        
        Used for comparing rates like CTR, conversion rate, etc.
        Uses Pingouin, statsmodels, or custom calculations with comprehensive error handling.
        
        Raises:
            ValueError: If input parameters are invalid
        """
        # Validate inputs
        self._validate_proportion_data(successes1, total1, "sample1")
        self._validate_proportion_data(successes2, total2, "sample2")
        
        try:
            # Calculate proportions
            p1 = successes1 / total1 if total1 > 0 else 0
            p2 = successes2 / total2 if total2 > 0 else 0
            
            # Perform z-test using available libraries
            # Try statsmodels first as it's specifically designed for proportion tests
            if STATSMODELS_AVAILABLE and total1 > 0 and total2 > 0:
                count = np.array([successes1, successes2])
                nobs = np.array([total1, total2])
                z_stat, p_value = proportions_ztest(count, nobs, alternative='two-sided')
                test_type = "Z-test for proportions (statsmodels)"
            else:
                # Fallback to custom calculation
                p_pool = (successes1 + successes2) / (total1 + total2) if (total1 + total2) > 0 else 0
                se = math.sqrt(p_pool * (1 - p_pool) * (1/total1 + 1/total2)) if p_pool > 0 and p_pool < 1 else 0
                z_stat = (p1 - p2) / se if se > 0 else 0
                p_value = self._z_to_p_value(abs(z_stat))
                test_type = "Z-test for proportions"
            
            # Effect size (Cohen's h)
            # Pingouin has compute_effsize for proportions as well
            if PINGOUIN_AVAILABLE:
                try:
                    effect_size = pg.compute_effsize(p1, p2, eftype='cohen-h')
                    effect_size = abs(effect_size)
                except Exception:
                    # Fallback to manual calculation
                    effect_size = self._cohens_h(p1, p2)
            else:
                effect_size = self._cohens_h(p1, p2)
            
            # Statistical power
            # Use Pingouin's power_ttest2n for two-sample proportions if available
            if PINGOUIN_AVAILABLE and effect_size > 0:
                try:
                    power = pg.power_ttest2n(
                        nx=total1,
                        ny=total2,
                        d=effect_size,
                        alpha=self.alpha,
                        alternative='two-sided'
                    )
                    power = max(0.0, min(1.0, power))  # Clamp to [0, 1]
                except Exception:
                    # Fallback to scipy or custom
                    if SCIPY_AVAILABLE:
                        power = self._calculate_power_scipy(effect_size, total1, total2)
                    else:
                        power = self._calculate_power(effect_size, total1 + total2)
            elif SCIPY_AVAILABLE:
                power = self._calculate_power_scipy(effect_size, total1, total2)
            else:
                power = self._calculate_power(effect_size, total1 + total2)
            
            # Sample size needed
            # Use Pingouin's power functions for sample size if available
            if PINGOUIN_AVAILABLE and effect_size > 0:
                try:
                    needed = pg.power_ttest(
                        d=effect_size,
                        power=0.80,
                        alpha=self.alpha,
                        alternative='two-sided'
                    )
                    needed = max(int(math.ceil(needed)), 100)
                except Exception:
                    # Fallback to scipy or custom
                    if SCIPY_AVAILABLE:
                        needed = self._calculate_sample_size_needed_scipy(effect_size, 0.80, self.alpha)
                    else:
                        needed = self._calculate_sample_size_needed(effect_size, 0.80, self.alpha)
            elif SCIPY_AVAILABLE:
                needed = self._calculate_sample_size_needed_scipy(effect_size, 0.80, self.alpha)
            else:
                needed = self._calculate_sample_size_needed(effect_size, 0.80, self.alpha)
            
            is_significant = p_value < self.alpha
            
            conclusion = self._generate_conclusion(
                is_significant, p_value, effect_size,
                p1 * 100, p2 * 100, "rate"
            )
            
            return StatisticalResult(
                is_significant=is_significant,
                p_value=p_value,
                confidence_level=self.confidence_level,
                effect_size=effect_size,
                power=power,
                sample_size_needed=needed,
                test_type=test_type,
                conclusion=conclusion
            )
        
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise RuntimeError(f"Error performing z-test: {str(e)}") from e
    
    def calculate_confidence_interval(
        self,
        mean: float,
        std: float,
        sample_size: int
    ) -> Tuple[float, float]:
        """Calculate confidence interval for a mean. Uses scipy if available."""
        if SCIPY_AVAILABLE and sample_size > 1:
            # Use scipy's t-distribution for small samples, normal for large
            if sample_size < 30:
                # Use t-distribution for small samples
                df = sample_size - 1
                t_critical = abs(t.ppf((1 - self.confidence_level) / 2, df))
                margin = t_critical * (std / math.sqrt(sample_size))
            else:
                # Use normal distribution for large samples
                z_critical = abs(norm.ppf((1 - self.confidence_level) / 2))
                margin = z_critical * (std / math.sqrt(sample_size))
        else:
            # Fallback to custom calculation
            se = std / math.sqrt(sample_size) if sample_size > 0 else 0
            z_critical = self._get_z_critical(self.confidence_level)
            margin = z_critical * se
        
        return (mean - margin, mean + margin)
    
    def calculate_minimum_sample_size(
        self,
        baseline_rate: float,
        expected_lift: float,
        power: float = 0.80
    ) -> int:
        """
        Calculate minimum sample size needed to detect an effect.
        
        Uses Pingouin's power functions when available for more accurate calculations.
        
        Args:
            baseline_rate: Current conversion/success rate (0-1)
            expected_lift: Expected improvement (e.g., 0.15 for 15% lift)
            power: Desired statistical power (default 0.80)
        
        Returns:
            Minimum sample size needed per variant
        
        Raises:
            ValueError: If input parameters are invalid
        """
        # Validate inputs
        self._validate_rate(baseline_rate, "baseline_rate")
        self._validate_numeric(expected_lift, "expected_lift", min_value=-1.0)
        self._validate_rate(power, "power")
        
        try:
            new_rate = baseline_rate * (1 + expected_lift)
            
            # Ensure new_rate is within valid bounds
            if new_rate < 0 or new_rate > 1:
                raise ValueError(
                    f"baseline_rate ({baseline_rate}) * (1 + expected_lift ({expected_lift})) "
                    f"must result in a rate between 0 and 1, got {new_rate}"
                )
            
            effect_size = self._cohens_h(baseline_rate, new_rate)
            
            # Use Pingouin for more accurate sample size calculation
            if PINGOUIN_AVAILABLE and effect_size > 0:
                try:
                    n = pg.power_ttest(
                        d=effect_size,
                        power=power,
                        alpha=self.alpha,
                        alternative='two-sided'
                    )
                    return max(int(math.ceil(n)), 100)  # Minimum 100 per variant
                except Exception:
                    # Fallback to custom calculation
                    pass
            
            # Fallback calculation
            z_alpha = self._get_z_critical(self.confidence_level)
            z_beta = self._get_z_critical(power)
            
            if effect_size > 0:
                n = ((z_alpha + z_beta) / effect_size) ** 2
                return max(int(math.ceil(n)), 100)  # Minimum 100 per variant
            else:
                # If effect size is 0, we can't detect a difference
                return 10000  # Large number indicating infeasibility
        
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise RuntimeError(f"Error calculating sample size: {str(e)}") from e
    
    def analyze_experiment_results(
        self,
        control_data: Dict,
        treatment_data: Dict,
        metric_type: str = "rate"
    ) -> StatisticalResult:
        """
        Analyze experiment results and determine statistical significance.
        
        Args:
            control_data: {'successes': int, 'total': int} or {'mean': float, 'std': float, 'size': int}
            treatment_data: Same format as control_data
            metric_type: 'rate' for proportions, 'continuous' for means
        
        Returns:
            StatisticalResult with significance testing results
        """
        if metric_type == "rate":
            return self.z_test_proportions(
                successes1=treatment_data['successes'],
                total1=treatment_data['total'],
                successes2=control_data['successes'],
                total2=control_data['total']
            )
        else:  # continuous
            return self.t_test_two_sample(
                sample1_mean=treatment_data['mean'],
                sample1_std=treatment_data['std'],
                sample1_size=treatment_data['size'],
                sample2_mean=control_data['mean'],
                sample2_std=control_data['std'],
                sample2_size=control_data['size']
            )
    
    # Helper methods
    
    def _calculate_welch_df(
        self,
        std1: float, n1: int,
        std2: float, n2: int
    ) -> float:
        """
        Calculate Welch-Satterthwaite degrees of freedom.
        
        Includes error handling for edge cases.
        """
        # Handle edge cases
        if n1 <= 1 or n2 <= 1:
            return 1.0
        
        if std1 == 0 and std2 == 0:
            return float(n1 + n2 - 2)
        
        try:
            s1_sq_n1 = (std1 ** 2) / n1
            s2_sq_n2 = (std2 ** 2) / n2
            
            numerator = (s1_sq_n1 + s2_sq_n2) ** 2
            denominator = (s1_sq_n1 ** 2) / (n1 - 1) + (s2_sq_n2 ** 2) / (n2 - 1)
            
            if denominator > 0 and math.isfinite(numerator) and math.isfinite(denominator):
                df = numerator / denominator
                return max(1.0, min(df, float(n1 + n2 - 2)))  # Clamp to reasonable range
            else:
                return 1.0
        except (ZeroDivisionError, OverflowError):
            return 1.0
    
    def _t_to_p_value(self, t: float, df: float) -> float:
        """Approximate p-value from t-statistic (two-tailed)."""
        # Simplified approximation using normal distribution for large df
        if df > 30:
            return self._z_to_p_value(t)
        
        # For small df, use a conservative estimate
        return min(2 * (1 - self._normal_cdf(abs(t))), 1.0)
    
    def _z_to_p_value(self, z: float) -> float:
        """Calculate two-tailed p-value from z-statistic."""
        return 2 * (1 - self._normal_cdf(abs(z)))
    
    def _normal_cdf(self, x: float) -> float:
        """Cumulative distribution function for standard normal distribution."""
        # Approximation using error function
        return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0
    
    def _get_z_critical(self, confidence: float) -> float:
        """Get critical z-value for confidence level."""
        # Common z-values
        z_table = {
            0.90: 1.645,
            0.95: 1.96,
            0.99: 2.576,
            0.80: 1.282
        }
        return z_table.get(confidence, 1.96)
    
    def _cohens_h(self, p1: float, p2: float) -> float:
        """
        Calculate Cohen's h effect size for proportions.
        
        Includes error handling for edge cases.
        """
        try:
            # Clamp proportions to [0, 1] to handle floating point errors
            p1 = max(0.0, min(1.0, p1))
            p2 = max(0.0, min(1.0, p2))
            
            phi1 = 2 * math.asin(math.sqrt(p1))
            phi2 = 2 * math.asin(math.sqrt(p2))
            
            result = abs(phi1 - phi2)
            
            # Check for NaN or infinity
            if not math.isfinite(result):
                return 0.0
            
            return result
        except (ValueError, OverflowError):
            return 0.0
    
    def _calculate_power(self, effect_size: float, total_n: int) -> float:
        """Approximate statistical power."""
        if effect_size == 0 or total_n == 0:
            return 0.0
        
        # Simplified power calculation
        ncp = effect_size * math.sqrt(total_n / 2)  # Non-centrality parameter
        z_alpha = self._get_z_critical(self.confidence_level)
        
        power = 1 - self._normal_cdf(z_alpha - ncp)
        return max(0.0, min(1.0, power))
    
    def _calculate_power_scipy(self, effect_size: float, n1: int, n2: int) -> float:
        """Calculate statistical power using scipy (more accurate)."""
        if not SCIPY_AVAILABLE or effect_size == 0 or n1 == 0 or n2 == 0:
            return self._calculate_power(effect_size, n1 + n2)
        
        try:
            from scipy.stats import norm
            
            # Calculate non-centrality parameter
            n = min(n1, n2)  # Use smaller sample size
            ncp = effect_size * math.sqrt(n / 2)
            
            # Critical value
            z_alpha = abs(norm.ppf((1 - self.confidence_level) / 2))
            
            # Power calculation
            power = 1 - norm.cdf(z_alpha - ncp) + norm.cdf(-z_alpha - ncp)
            return max(0.0, min(1.0, power))
        except:
            # Fallback to custom calculation
            return self._calculate_power(effect_size, n1 + n2)
    
    def _calculate_sample_size_needed(
        self,
        effect_size: float,
        power: float,
        alpha: float
    ) -> int:
        """Calculate sample size needed per group."""
        if effect_size == 0:
            return 10000  # Large number if no effect
        
        z_alpha = self._get_z_critical(1 - alpha)
        z_beta = self._get_z_critical(power)
        
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        return max(int(math.ceil(n)), 100)
    
    def _calculate_sample_size_needed_scipy(
        self,
        effect_size: float,
        power: float,
        alpha: float
    ) -> int:
        """Calculate sample size needed using scipy (more accurate)."""
        if not SCIPY_AVAILABLE or effect_size == 0:
            return self._calculate_sample_size_needed(effect_size, power, alpha)
        
        try:
            from scipy.stats import norm
            
            z_alpha = abs(norm.ppf(alpha / 2))  # Two-tailed
            z_beta = abs(norm.ppf(1 - power))
            
            # Sample size calculation for two-sample test
            n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
            return max(int(math.ceil(n)), 100)
        except:
            # Fallback to custom calculation
            return self._calculate_sample_size_needed(effect_size, power, alpha)
    
    def _generate_conclusion(
        self,
        is_significant: bool,
        p_value: float,
        effect_size: float,
        value1: float,
        value2: float,
        metric_type: str
    ) -> str:
        """
        Generate human-readable conclusion.
        
        Includes error handling for invalid values (NaN, infinity, etc.).
        """
        try:
            parts = []
            
            # Handle NaN or infinity in p_value
            if not math.isfinite(p_value):
                p_value = 1.0  # Default to no significance
            
            if is_significant:
                parts.append(f"✓ Statistically significant difference detected (p={p_value:.4f}).")
            else:
                parts.append(f"✗ No statistically significant difference found (p={p_value:.4f}).")
            
            # Calculate change with error handling
            if value2 != 0 and math.isfinite(value1) and math.isfinite(value2):
                change = ((value1 - value2) / value2 * 100)
                if not math.isfinite(change):
                    change = 0
            else:
                change = 0
            
            direction = "increase" if change > 0 else "decrease"
            
            parts.append(
                f"Treatment shows {abs(change):.1f}% {direction} "
                f"({'significant' if is_significant else 'not significant'})."
            )
            
            # Effect size interpretation with error handling
            if not math.isfinite(effect_size):
                effect_size = 0.0
            
            if effect_size < 0.2:
                effect_desc = "small"
            elif effect_size < 0.5:
                effect_desc = "medium"
            else:
                effect_desc = "large"
            
            parts.append(f"Effect size: {effect_size:.3f} ({effect_desc}).")
            
            return " ".join(parts)
        except Exception:
            # Fallback to a basic conclusion if anything goes wrong
            return "Statistical test completed. Please review raw values for interpretation."


def quick_significance_test(
    control_value: float,
    control_size: int,
    treatment_value: float,
    treatment_size: int,
    metric_type: str = "rate"
) -> Dict:
    """
    Quick significance test helper function.
    
    Returns a simple dict with significance results.
    """
    engine = StatisticsEngine()
    
    if metric_type == "rate":
        # Treat values as proportions
        result = engine.z_test_proportions(
            successes1=int(treatment_value * treatment_size),
            total1=treatment_size,
            successes2=int(control_value * control_size),
            total2=control_size
        )
    else:
        # Would need std dev for t-test, use simplified approach
        # Assume 10% coefficient of variation
        control_std = control_value * 0.1
        treatment_std = treatment_value * 0.1
        
        result = engine.t_test_two_sample(
            sample1_mean=treatment_value,
            sample1_std=treatment_std,
            sample1_size=treatment_size,
            sample2_mean=control_value,
            sample2_std=control_std,
            sample2_size=control_size
        )
    
    return {
        'is_significant': result.is_significant,
        'p_value': result.p_value,
        'effect_size': result.effect_size,
        'conclusion': result.conclusion
    }





