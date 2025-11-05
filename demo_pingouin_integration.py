#!/usr/bin/env python3
"""
Demonstration of the enhanced statistics engine with Pingouin integration.

This script shows:
1. Normal usage (backward compatible)
2. Input validation catching errors
3. Robust error handling
"""

from statistics_engine import StatisticsEngine

print("=" * 70)
print("Statistics Engine with Pingouin Integration - Demo")
print("=" * 70)

# Initialize the engine
engine = StatisticsEngine(confidence_level=0.95)

print("\n1. NORMAL T-TEST (Backward Compatible)")
print("-" * 70)
result = engine.t_test_two_sample(
    sample1_mean=100, sample1_std=15, sample1_size=50,
    sample2_mean=85, sample2_std=12, sample2_size=50
)
print(f"Test Type: {result.test_type}")
print(f"Significant: {result.is_significant}")
print(f"P-value: {result.p_value:.6f}")
print(f"Effect Size: {result.effect_size:.4f}")
print(f"Power: {result.power:.4f}")
print(f"Sample Size Needed: {result.sample_size_needed}")
print(f"\nConclusion: {result.conclusion}")

print("\n2. NORMAL Z-TEST FOR PROPORTIONS")
print("-" * 70)
result = engine.z_test_proportions(
    successes1=150, total1=1000,
    successes2=100, total2=1000
)
print(f"Test Type: {result.test_type}")
print(f"Significant: {result.is_significant}")
print(f"P-value: {result.p_value:.6f}")
print(f"Effect Size: {result.effect_size:.4f}")
print(f"\nConclusion: {result.conclusion}")

print("\n3. SAMPLE SIZE CALCULATION")
print("-" * 70)
sample_size = engine.calculate_minimum_sample_size(
    baseline_rate=0.05,
    expected_lift=0.20,
    power=0.80
)
print(f"To detect a 20% lift from 5% baseline with 80% power:")
print(f"Required sample size per variant: {sample_size}")

print("\n4. INPUT VALIDATION (Error Handling)")
print("-" * 70)

# Test 1: Negative standard deviation
print("\nTest invalid input (negative std):")
try:
    engine.t_test_two_sample(
        sample1_mean=100, sample1_std=-5,  # Invalid!
        sample1_size=50, sample2_mean=85,
        sample2_std=12, sample2_size=50
    )
except ValueError as e:
    print(f"✓ Caught error: {e}")

# Test 2: Successes exceed total
print("\nTest invalid proportion (successes > total):")
try:
    engine.z_test_proportions(
        successes1=150, total1=100,  # Invalid!
        successes2=100, total2=1000
    )
except ValueError as e:
    print(f"✓ Caught error: {e}")

# Test 3: Invalid rate
print("\nTest invalid baseline rate (> 1):")
try:
    engine.calculate_minimum_sample_size(
        baseline_rate=1.5,  # Invalid!
        expected_lift=0.20,
        power=0.80
    )
except ValueError as e:
    print(f"✓ Caught error: {e}")

print("\n5. EDGE CASES (Robust Handling)")
print("-" * 70)

# Test with very small effect
print("\nSmall effect size test:")
result = engine.z_test_proportions(
    successes1=101, total1=1000,
    successes2=100, total2=1000
)
print(f"P-value: {result.p_value:.4f}")
print(f"Significant: {result.is_significant}")
print(f"Effect Size: {result.effect_size:.6f} (very small)")

# Test with zero successes
print("\nZero successes test:")
result = engine.z_test_proportions(
    successes1=0, total1=100,
    successes2=0, total2=100
)
print(f"P-value: {result.p_value:.4f}")
print(f"Significant: {result.is_significant}")
print(f"Effect Size: {result.effect_size:.6f}")

print("\n" + "=" * 70)
print("Demo completed successfully!")
print("All features working with backward compatibility maintained.")
print("=" * 70)

