"""Unit tests for statistical analysis engine."""

import unittest
import math
from statistics_engine import (
    StatisticsEngine, 
    StatisticalResult, 
    quick_significance_test,
    PINGOUIN_AVAILABLE,
    SCIPY_AVAILABLE,
    STATSMODELS_AVAILABLE
)


class TestStatisticsEngine(unittest.TestCase):
    """Test cases for StatisticsEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = StatisticsEngine(confidence_level=0.95)
    
    def test_initialization(self):
        """Test engine initialization with different confidence levels."""
        engine_90 = StatisticsEngine(confidence_level=0.90)
        self.assertEqual(engine_90.confidence_level, 0.90)
        self.assertAlmostEqual(engine_90.alpha, 0.10, places=5)
        
        engine_99 = StatisticsEngine(confidence_level=0.99)
        self.assertEqual(engine_99.confidence_level, 0.99)
        self.assertAlmostEqual(engine_99.alpha, 0.01, places=5)
    
    def test_z_test_significant_difference(self):
        """Test Z-test with significant difference in proportions."""
        # Treatment: 15% CTR (150/1000), Control: 10% CTR (100/1000)
        result = self.engine.z_test_proportions(
            successes1=150,
            total1=1000,
            successes2=100,
            total2=1000
        )
        
        self.assertIsInstance(result, StatisticalResult)
        self.assertTrue(result.is_significant)
        self.assertLess(result.p_value, 0.05)
        self.assertGreater(result.effect_size, 0)
        # Test type may vary if statsmodels/scipy is available
        self.assertIn("Z-test for proportions", result.test_type)
    
    def test_z_test_no_difference(self):
        """Test Z-test with no significant difference."""
        # Both groups have 10% CTR
        result = self.engine.z_test_proportions(
            successes1=100,
            total1=1000,
            successes2=101,
            total2=1000
        )
        
        self.assertFalse(result.is_significant)
        self.assertGreater(result.p_value, 0.05)
        self.assertLess(result.effect_size, 0.1)
    
    def test_z_test_edge_cases(self):
        """Test Z-test with edge cases."""
        # Zero successes
        result = self.engine.z_test_proportions(
            successes1=0,
            total1=100,
            successes2=0,
            total2=100
        )
        self.assertIsInstance(result, StatisticalResult)
        
        # Perfect conversion
        result = self.engine.z_test_proportions(
            successes1=100,
            total1=100,
            successes2=90,
            total2=100
        )
        self.assertTrue(result.is_significant)
    
    def test_t_test_significant_difference(self):
        """Test t-test with significant difference in means."""
        result = self.engine.t_test_two_sample(
            sample1_mean=100,
            sample1_std=15,
            sample1_size=50,
            sample2_mean=85,
            sample2_std=12,
            sample2_size=50
        )
        
        self.assertIsInstance(result, StatisticalResult)
        self.assertTrue(result.is_significant)
        # Test type may vary if scipy is available
        self.assertIn("Two-sample t-test", result.test_type)
    
    def test_t_test_no_difference(self):
        """Test t-test with no significant difference."""
        result = self.engine.t_test_two_sample(
            sample1_mean=100,
            sample1_std=15,
            sample1_size=50,
            sample2_mean=99,
            sample2_std=15,
            sample2_size=50
        )
        
        self.assertFalse(result.is_significant)
    
    def test_confidence_interval_calculation(self):
        """Test confidence interval calculation."""
        mean = 100
        std = 15
        n = 50
        
        lower, upper = self.engine.calculate_confidence_interval(mean, std, n)
        
        self.assertLess(lower, mean)
        self.assertGreater(upper, mean)
        # CI should be approximately symmetric around mean
        # (may use t-distribution for small samples, so allow wider tolerance)
        margin = (upper - lower) / 2
        self.assertAlmostEqual(mean - lower, margin, delta=5)
        self.assertAlmostEqual(upper - mean, margin, delta=5)
    
    def test_sample_size_calculation(self):
        """Test sample size calculator."""
        # Need to detect 20% improvement in 5% baseline
        sample_size = self.engine.calculate_minimum_sample_size(
            baseline_rate=0.05,
            expected_lift=0.20,
            power=0.80
        )
        
        self.assertIsInstance(sample_size, int)
        self.assertGreater(sample_size, 100)  # Should be substantial
        self.assertLess(sample_size, 100000)  # But reasonable
    
    def test_sample_size_with_different_powers(self):
        """Test sample size calculation with different power levels."""
        size_80 = self.engine.calculate_minimum_sample_size(0.05, 0.20, 0.80)
        size_90 = self.engine.calculate_minimum_sample_size(0.05, 0.20, 0.90)
        
        # Higher power requires more samples
        self.assertGreater(size_90, size_80)
    
    def test_effect_size_calculations(self):
        """Test effect size calculations."""
        # Small difference in proportions
        small_diff = self.engine._cohens_h(0.10, 0.11)
        self.assertLess(small_diff, 0.1)
        
        # Large difference
        large_diff = self.engine._cohens_h(0.10, 0.30)
        self.assertGreater(large_diff, 0.3)
    
    def test_analyze_experiment_results_rate(self):
        """Test experiment analysis with rate metrics."""
        control = {'successes': 100, 'total': 1000}
        treatment = {'successes': 150, 'total': 1000}
        
        result = self.engine.analyze_experiment_results(
            control_data=control,
            treatment_data=treatment,
            metric_type='rate'
        )
        
        self.assertTrue(result.is_significant)
        self.assertLess(result.p_value, 0.05)
    
    def test_analyze_experiment_results_continuous(self):
        """Test experiment analysis with continuous metrics."""
        control = {'mean': 85, 'std': 12, 'size': 50}
        treatment = {'mean': 100, 'std': 15, 'size': 50}
        
        result = self.engine.analyze_experiment_results(
            control_data=control,
            treatment_data=treatment,
            metric_type='continuous'
        )
        
        self.assertTrue(result.is_significant)
    
    def test_quick_significance_test(self):
        """Test quick significance test helper function."""
        result = quick_significance_test(
            control_value=0.10,
            control_size=1000,
            treatment_value=0.15,
            treatment_size=1000,
            metric_type='rate'
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('is_significant', result)
        self.assertIn('p_value', result)
        self.assertIn('effect_size', result)
        self.assertTrue(result['is_significant'])


class TestStatisticalHelpers(unittest.TestCase):
    """Test helper methods in StatisticsEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = StatisticsEngine()
    
    def test_normal_cdf(self):
        """Test normal CDF approximation."""
        # Test known values
        self.assertAlmostEqual(self.engine._normal_cdf(0), 0.5, places=2)
        self.assertAlmostEqual(self.engine._normal_cdf(1.96), 0.975, places=2)
        self.assertAlmostEqual(self.engine._normal_cdf(-1.96), 0.025, places=2)
    
    def test_z_critical_values(self):
        """Test z-critical value lookup."""
        self.assertEqual(self.engine._get_z_critical(0.95), 1.96)
        self.assertEqual(self.engine._get_z_critical(0.90), 1.645)
        self.assertEqual(self.engine._get_z_critical(0.99), 2.576)
    
    def test_welch_df_calculation(self):
        """Test Welch-Satterthwaite degrees of freedom."""
        df = self.engine._calculate_welch_df(
            std1=15, n1=50,
            std2=12, n2=50
        )
        
        self.assertIsInstance(df, float)
        self.assertGreater(df, 0)
        self.assertLess(df, 100)
    
    def test_power_calculation(self):
        """Test statistical power calculation."""
        # Large effect size should give high power
        power_large = self.engine._calculate_power(effect_size=0.8, total_n=100)
        self.assertGreater(power_large, 0.5)
        
        # Small effect size should give low power with small sample
        power_small = self.engine._calculate_power(effect_size=0.1, total_n=50)
        self.assertLess(power_small, 0.5)


class TestInputValidation(unittest.TestCase):
    """Test input validation for StatisticsEngine."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = StatisticsEngine(confidence_level=0.95)
    
    def test_validate_sample_data_negative_size(self):
        """Test that negative sample size raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_sample_data(100, 15, -10, "test")
        self.assertIn("must be a positive integer", str(context.exception))
    
    def test_validate_sample_data_zero_size(self):
        """Test that zero sample size raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_sample_data(100, 15, 0, "test")
        self.assertIn("must be a positive integer", str(context.exception))
    
    def test_validate_sample_data_negative_std(self):
        """Test that negative std raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_sample_data(100, -15, 50, "test")
        self.assertIn("must be non-negative", str(context.exception))
    
    def test_validate_sample_data_infinite_mean(self):
        """Test that infinite mean raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_sample_data(float('inf'), 15, 50, "test")
        self.assertIn("must be a finite number", str(context.exception))
    
    def test_validate_sample_data_nan_std(self):
        """Test that NaN std raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_sample_data(100, float('nan'), 50, "test")
        self.assertIn("must be a finite number", str(context.exception))
    
    def test_validate_proportion_data_negative_successes(self):
        """Test that negative successes raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_proportion_data(-5, 100, "test")
        self.assertIn("must be a non-negative integer", str(context.exception))
    
    def test_validate_proportion_data_successes_exceed_total(self):
        """Test that successes > total raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_proportion_data(150, 100, "test")
        self.assertIn("cannot exceed", str(context.exception))
    
    def test_validate_proportion_data_zero_total(self):
        """Test that zero total raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_proportion_data(0, 0, "test")
        self.assertIn("must be a positive integer", str(context.exception))
    
    def test_validate_confidence_level_invalid(self):
        """Test that invalid confidence level raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_confidence_level(1.5)
        self.assertIn("must be between 0 and 1", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.engine._validate_confidence_level(0)
        self.assertIn("must be between 0 and 1", str(context.exception))
    
    def test_validate_rate_out_of_bounds(self):
        """Test that rate outside [0,1] raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_rate(1.5, "test_rate")
        self.assertIn("must be between 0 and 1", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            self.engine._validate_rate(-0.1, "test_rate")
        self.assertIn("must be between 0 and 1", str(context.exception))
    
    def test_validate_rate_infinite(self):
        """Test that infinite rate raises ValueError."""
        with self.assertRaises(ValueError) as context:
            self.engine._validate_rate(float('inf'), "test_rate")
        self.assertIn("must be a finite number", str(context.exception))
    
    def test_t_test_with_invalid_inputs(self):
        """Test t_test_two_sample with invalid inputs."""
        with self.assertRaises(ValueError):
            self.engine.t_test_two_sample(
                sample1_mean=100,
                sample1_std=-5,  # Invalid negative std
                sample1_size=50,
                sample2_mean=85,
                sample2_std=12,
                sample2_size=50
            )
    
    def test_z_test_with_invalid_inputs(self):
        """Test z_test_proportions with invalid inputs."""
        with self.assertRaises(ValueError):
            self.engine.z_test_proportions(
                successes1=150,
                total1=100,  # Invalid: successes > total
                successes2=100,
                total2=1000
            )
    
    def test_calculate_minimum_sample_size_invalid_baseline(self):
        """Test calculate_minimum_sample_size with invalid baseline rate."""
        with self.assertRaises(ValueError):
            self.engine.calculate_minimum_sample_size(
                baseline_rate=1.5,  # Invalid: > 1
                expected_lift=0.20,
                power=0.80
            )
    
    def test_calculate_minimum_sample_size_invalid_lift(self):
        """Test calculate_minimum_sample_size with invalid expected lift."""
        with self.assertRaises(ValueError):
            self.engine.calculate_minimum_sample_size(
                baseline_rate=0.5,
                expected_lift=1.5,  # Results in rate > 1
                power=0.80
            )


class TestPingouinIntegration(unittest.TestCase):
    """Test Pingouin integration and library availability."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = StatisticsEngine()
    
    def test_library_availability_flags(self):
        """Test that library availability flags are set correctly."""
        # These should be boolean values
        self.assertIsInstance(PINGOUIN_AVAILABLE, bool)
        self.assertIsInstance(SCIPY_AVAILABLE, bool)
        self.assertIsInstance(STATSMODELS_AVAILABLE, bool)
    
    @unittest.skipIf(not PINGOUIN_AVAILABLE, "Pingouin not installed")
    def test_pingouin_effect_size_calculation(self):
        """Test that Pingouin is used for effect size when available."""
        result = self.engine.t_test_two_sample(
            sample1_mean=100, sample1_std=15, sample1_size=50,
            sample2_mean=85, sample2_std=12, sample2_size=50
        )
        
        # Should have valid effect size
        self.assertIsInstance(result.effect_size, float)
        self.assertGreater(result.effect_size, 0)
        self.assertTrue(math.isfinite(result.effect_size))
    
    @unittest.skipIf(not PINGOUIN_AVAILABLE, "Pingouin not installed")
    def test_pingouin_power_calculation(self):
        """Test that Pingouin is used for power analysis when available."""
        result = self.engine.t_test_two_sample(
            sample1_mean=100, sample1_std=15, sample1_size=50,
            sample2_mean=85, sample2_std=12, sample2_size=50
        )
        
        # Should have valid power between 0 and 1
        self.assertIsInstance(result.power, float)
        self.assertGreaterEqual(result.power, 0.0)
        self.assertLessEqual(result.power, 1.0)
    
    @unittest.skipIf(not PINGOUIN_AVAILABLE, "Pingouin not installed")
    def test_pingouin_sample_size_calculation(self):
        """Test that Pingouin is used for sample size when available."""
        sample_size = self.engine.calculate_minimum_sample_size(
            baseline_rate=0.05,
            expected_lift=0.20,
            power=0.80
        )
        
        # Should return reasonable sample size
        self.assertIsInstance(sample_size, int)
        self.assertGreater(sample_size, 0)
        self.assertLess(sample_size, 1000000)
    
    @unittest.skipIf(not PINGOUIN_AVAILABLE, "Pingouin not installed")
    def test_pingouin_cohens_h_for_proportions(self):
        """Test Cohen's h calculation with Pingouin for proportions."""
        result = self.engine.z_test_proportions(
            successes1=150, total1=1000,
            successes2=100, total2=1000
        )
        
        # Should have valid effect size
        self.assertIsInstance(result.effect_size, float)
        self.assertGreaterEqual(result.effect_size, 0.0)
        self.assertTrue(math.isfinite(result.effect_size))
    
    def test_fallback_when_pingouin_unavailable(self):
        """Test that calculations work even without Pingouin."""
        # This should work regardless of Pingouin availability
        result = self.engine.t_test_two_sample(
            sample1_mean=100, sample1_std=15, sample1_size=50,
            sample2_mean=85, sample2_std=12, sample2_size=50
        )
        
        # Should get valid results either way
        self.assertIsInstance(result, StatisticalResult)
        self.assertIsInstance(result.p_value, float)
        self.assertIsInstance(result.effect_size, float)
        self.assertIsInstance(result.power, float)
    
    def test_test_type_indicates_library_used(self):
        """Test that test_type string indicates which library was used."""
        result = self.engine.t_test_two_sample(
            sample1_mean=100, sample1_std=15, sample1_size=50,
            sample2_mean=85, sample2_std=12, sample2_size=50
        )
        
        # Should indicate test type
        self.assertIn("t-test", result.test_type.lower())
        
        # If scipy is available, should indicate it
        if SCIPY_AVAILABLE:
            self.assertIn("scipy", result.test_type.lower())
    
    def test_z_test_indicates_library_used(self):
        """Test that z-test indicates which library was used."""
        result = self.engine.z_test_proportions(
            successes1=150, total1=1000,
            successes2=100, total2=1000
        )
        
        # Should indicate test type
        self.assertIn("z-test", result.test_type.lower())
        self.assertIn("proportion", result.test_type.lower())


class TestErrorHandling(unittest.TestCase):
    """Test error handling in helper methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.engine = StatisticsEngine()
    
    def test_welch_df_with_small_samples(self):
        """Test Welch df calculation with sample size of 1."""
        df = self.engine._calculate_welch_df(10, 1, 12, 50)
        self.assertEqual(df, 1.0)  # Should return default for n<=1
    
    def test_welch_df_with_zero_stds(self):
        """Test Welch df calculation with zero standard deviations."""
        df = self.engine._calculate_welch_df(0, 50, 0, 50)
        self.assertIsInstance(df, float)
        self.assertGreater(df, 0)
    
    def test_cohens_h_with_edge_values(self):
        """Test Cohen's h with edge case values."""
        # Both proportions at 0
        h = self.engine._cohens_h(0.0, 0.0)
        self.assertEqual(h, 0.0)
        
        # Both proportions at 1
        h = self.engine._cohens_h(1.0, 1.0)
        self.assertEqual(h, 0.0)
        
        # One at 0, one at 1 (maximum difference)
        h = self.engine._cohens_h(0.0, 1.0)
        self.assertGreater(h, 0)
    
    def test_cohens_h_with_slightly_out_of_bounds(self):
        """Test Cohen's h handles slightly out-of-bounds values (floating point errors)."""
        # Should clamp and not raise error
        h = self.engine._cohens_h(1.0001, 0.5)
        self.assertIsInstance(h, float)
        self.assertGreaterEqual(h, 0.0)
    
    def test_generate_conclusion_with_zero_denominator(self):
        """Test conclusion generation with zero baseline value."""
        conclusion = self.engine._generate_conclusion(
            is_significant=True,
            p_value=0.01,
            effect_size=0.5,
            value1=10.0,
            value2=0.0,  # Zero denominator
            metric_type="rate"
        )
        self.assertIsInstance(conclusion, str)
        self.assertIn("significant", conclusion.lower())
    
    def test_generate_conclusion_with_nan_values(self):
        """Test conclusion generation with NaN values."""
        conclusion = self.engine._generate_conclusion(
            is_significant=False,
            p_value=float('nan'),
            effect_size=float('nan'),
            value1=float('nan'),
            value2=10.0,
            metric_type="rate"
        )
        self.assertIsInstance(conclusion, str)
        # Should not crash and return some conclusion
        self.assertGreater(len(conclusion), 0)
    
    def test_generate_conclusion_with_infinity(self):
        """Test conclusion generation with infinity values."""
        conclusion = self.engine._generate_conclusion(
            is_significant=False,
            p_value=0.5,
            effect_size=float('inf'),
            value1=float('inf'),
            value2=10.0,
            metric_type="rate"
        )
        self.assertIsInstance(conclusion, str)
        self.assertGreater(len(conclusion), 0)


if __name__ == '__main__':
    unittest.main()

