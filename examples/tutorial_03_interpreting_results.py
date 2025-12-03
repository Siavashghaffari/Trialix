"""
Tutorial 3: Interpreting Statistical Results Like a Pro
========================================================

In this tutorial, you'll learn:
- How to interpret odds ratios and confidence intervals
- What AUC really means and when to trust it
- How to explain p-values to non-statisticians
- How to identify false positives and overfitting
- How to validate your enrichment strategy

Scenario: You've run your analysis and got results. Now you need to:
1. Understand what the statistics really mean
2. Identify which results are trustworthy
3. Explain findings to clinical team
4. Defend your recommendations to regulators
"""

from trialix import TrialEnrichment
import pandas as pd
import numpy as np

print("=" * 80)
print("TUTORIAL 3: Interpreting Statistical Results Like a Pro")
print("=" * 80)
print()

# ==============================================================================
# SETUP
# ==============================================================================
print("Let's run a standard analysis first:")
print()

analyzer = TrialEnrichment(data="examples/oncology_trial.csv", outcome="outcome")
summary = analyzer.load_data()
biomarkers = analyzer.find_biomarkers(top_n=10, min_auc=0.50)
cutoffs = analyzer.optimize_cutoffs()

print(f"Analysis complete: Found {len(biomarkers)} biomarkers")
print()
input("Press Enter to start interpretation guide...")
print()

# ==============================================================================
# PART 1: Understanding Odds Ratios
# ==============================================================================
print("PART 1: Understanding Odds Ratios (OR)")
print("=" * 80)
print()

print("What is an Odds Ratio?")
print("-" * 80)
print()
print("An OR tells you how much a biomarker changes the ODDS of response.")
print()
print("Example from your data:")
for idx, row in biomarkers.head(3).iterrows():
    print(f"\n{row['biomarker']}: OR = {row['OR']:.2f}")

    if row['OR'] > 1:
        # Calculate percentage increase in odds
        pct_increase = (row['OR'] - 1) * 100
        print(f"  → For every 1-unit increase in {row['biomarker']},")
        print(f"     the ODDS of response increase by {pct_increase:.0f}%")

        # Practical interpretation
        if row['OR'] > 2:
            print(f"  → This is a STRONG positive association")
        elif row['OR'] > 1.5:
            print(f"  → This is a MODERATE positive association")
        else:
            print(f"  → This is a WEAK positive association")

    elif row['OR'] < 1:
        pct_decrease = (1 - row['OR']) * 100
        print(f"  → Higher {row['biomarker']} DECREASES odds by {pct_decrease:.0f}%")
    else:
        print(f"  → No association with response")

print()
print("Common Misinterpretation:")
print("-" * 80)
print("❌ WRONG: 'OR=2 means 2x higher response rate'")
print("✓ RIGHT: 'OR=2 means 2x higher ODDS, not necessarily 2x rate'")
print()
print("Why it matters:")
print("  If baseline response is 40%:")
print("    • Baseline odds = 0.40/0.60 = 0.67")
print("    • With OR=2, new odds = 1.33")
print("    • New response rate = 1.33/(1+1.33) = 57% (NOT 80%!)")
print()

input("Press Enter to continue...")
print()

# ==============================================================================
# PART 2: Confidence Intervals - The Uncertainty Story
# ==============================================================================
print("PART 2: Confidence Intervals - The Uncertainty Story")
print("=" * 80)
print()

print("What are 95% Confidence Intervals?")
print("-" * 80)
print()
print("The 95% CI tells you: 'We're 95% confident the TRUE effect is in this range'")
print()

for idx, row in biomarkers.head(3).iterrows():
    print(f"\n{row['biomarker']}")
    print(f"  OR = {row['OR']:.2f}   [95% CI: {row['CI_lower']:.2f} - {row['CI_upper']:.2f}]")

    ci_width = row['CI_upper'] - row['CI_lower']

    # Check if CI crosses 1
    if row['CI_lower'] > 1:
        print(f"  ✓ CI doesn't cross 1 → Statistically significant positive effect")
    elif row['CI_upper'] < 1:
        print(f"  ✓ CI doesn't cross 1 → Statistically significant negative effect")
    else:
        print(f"  ⚠️  CI crosses 1 → NOT statistically significant")

    # Assess precision
    if ci_width < 1:
        print(f"  ✓ Narrow CI ({ci_width:.2f}) → Precise estimate")
    elif ci_width < 3:
        print(f"  ⚠️  Moderate CI ({ci_width:.2f}) → Some uncertainty")
    else:
        print(f"  ❌ Wide CI ({ci_width:.2f}) → High uncertainty, need more data")

print()
print("Rule of Thumb:")
print("-" * 80)
print("  Narrow CI = More patients or stronger effect = More confidence")
print("  Wide CI = Fewer patients or weaker effect = Less confidence")
print()

input("Press Enter to continue...")
print()

# ==============================================================================
# PART 3: P-Values - What They REALLY Mean
# ==============================================================================
print("PART 3: P-Values - What They REALLY Mean")
print("=" * 80)
print()

print("The Truth About P-Values:")
print("-" * 80)
print()
print("A p-value answers: 'If there was NO real effect, how likely would we")
print("see results this extreme just by chance?'")
print()

for idx, row in biomarkers.head(3).iterrows():
    print(f"\n{row['biomarker']}: p = {row['p_value']:.4f}")

    if row['p_value'] < 0.001:
        print(f"  → Less than 0.1% chance this is random")
        print(f"  → Extremely strong evidence")
        print(f"  → Safe to trust this biomarker")
    elif row['p_value'] < 0.01:
        print(f"  → Less than 1% chance this is random")
        print(f"  → Strong evidence")
        print(f"  → Likely a real effect")
    elif row['p_value'] < 0.05:
        print(f"  → Less than 5% chance this is random")
        print(f"  → Statistically significant")
        print(f"  → Consider with caution")
    else:
        print(f"  → More than 5% chance this is random")
        print(f"  → NOT statistically significant")
        print(f"  → Don't trust this biomarker")

print()
print("What P-Values DON'T Tell You:")
print("-" * 80)
print("  ❌ How important the effect is (use OR for that)")
print("  ❌ Probability the hypothesis is true (it's NOT that!)")
print("  ❌ If it will replicate in new patients")
print("  ❌ If it's clinically meaningful")
print()

print("The Multiple Testing Problem:")
print("-" * 80)
print(f"You tested {len(biomarkers)} biomarkers at p < 0.05")
print(f"Expected false positives: {len(biomarkers) * 0.05:.1f}")
print()
print("⚠️  WARNING: Some 'significant' biomarkers may be false positives!")
print()
print("Protection strategies:")
print("  1. Use stricter threshold (p < 0.01)")
print("  2. Focus on biomarkers with biological rationale")
print("  3. Validate in independent dataset")
print("  4. Look for consistent effects across related biomarkers")
print()

input("Press Enter to continue...")
print()

# ==============================================================================
# PART 4: AUC - The Predictive Power Metric
# ==============================================================================
print("PART 4: AUC - The Predictive Power Metric")
print("=" * 80)
print()

print("What is AUC?")
print("-" * 80)
print()
print("AUC (Area Under ROC Curve) = Probability that a random responder")
print("has a higher biomarker value than a random non-responder")
print()

print("AUC Interpretation Guide:")
print()
print("  AUC = 1.00  → Perfect prediction (never happens in reality)")
print("  AUC = 0.90  → Excellent (very rare in clinical trials)")
print("  AUC = 0.80  → Good (publishable, clinically useful)")
print("  AUC = 0.70  → Fair (useful for enrichment)")
print("  AUC = 0.60  → Poor (marginal utility)")
print("  AUC = 0.50  → Random (no predictive value)")
print()

for idx, row in biomarkers.head(5).iterrows():
    auc = row['AUC']
    print(f"{row['biomarker']}: AUC = {auc:.2f}")

    if auc >= 0.80:
        print(f"  ✓ EXCELLENT - Strong candidate for enrichment")
        print(f"  → Can reliably separate responders from non-responders")
    elif auc >= 0.70:
        print(f"  ✓ GOOD - Useful for enrichment")
        print(f"  → Moderate separation, consider combining with other biomarkers")
    elif auc >= 0.60:
        print(f"  ⚠️  FAIR - Marginal utility")
        print(f"  → Weak separation, use only if no better options")
    else:
        print(f"  ❌ POOR - Not useful")
        print(f"  → Too close to random, don't use for enrichment")
    print()

print("Practical Example:")
print("-" * 80)
best_biomarker = biomarkers.iloc[0]
auc = best_biomarker['AUC']
print(f"\n{best_biomarker['biomarker']} has AUC = {auc:.2f}")
print()
print("This means:")
print(f"  • If you pick a random responder and random non-responder,")
print(f"    there's a {auc:.0%} chance the responder has higher {best_biomarker['biomarker']}")
print(f"  • {(1-auc)*100:.0f}% of the time, they overlap")
print(f"  • This {('is' if auc >= 0.70 else 'may not be')} good enough for enrichment")
print()

input("Press Enter to continue...")
print()

# ==============================================================================
# PART 5: Sample Size Matters
# ==============================================================================
print("PART 5: Sample Size Matters - When to Trust Your Results")
print("=" * 80)
print()

print("Your Analysis:")
print(f"  Total patients: {summary.n_patients}")
print(f"  Responders: {summary.n_responders}")
print(f"  Non-responders: {summary.n_non_responders}")
print()

# Check if sample size is adequate
min_per_group = 30
if summary.n_responders < min_per_group or summary.n_non_responders < min_per_group:
    print("⚠️  WARNING: Small sample size!")
    print()
    print("Risks:")
    print("  • Results may not replicate in larger datasets")
    print("  • Wider confidence intervals = more uncertainty")
    print("  • Higher chance of false positives")
    print()
    print("Recommendations:")
    print("  ✓ Focus on biomarkers with very strong effects (OR > 3)")
    print("  ✓ Require stricter p-values (p < 0.01)")
    print("  ✓ Validate findings in external dataset")
    print("  ✓ Consider biological plausibility heavily")
else:
    print("✓ Adequate sample size for reliable estimates")
    print()
    print("You can trust:")
    print("  ✓ Biomarkers with p < 0.05")
    print("  ✓ AUC values are reasonably stable")
    print("  ✓ Confidence intervals are informative")

print()
print("Rule of Thumb for Sample Size:")
print("-" * 80)
print("  • N < 50: Very risky, pilot data only")
print("  • N = 50-100: Adequate for hypothesis generation")
print("  • N = 100-300: Good for enrichment strategy")
print("  • N > 300: Excellent, results likely to replicate")
print()

input("Press Enter to continue...")
print()

# ==============================================================================
# PART 6: Red Flags - When NOT to Trust Results
# ==============================================================================
print("PART 6: Red Flags - When NOT to Trust Results")
print("=" * 80)
print()

print("Checking for red flags in your analysis...")
print()

red_flags = []

# Check 1: Too many biomarkers tested
if len(biomarkers) > 20:
    red_flags.append("Testing many biomarkers without correction")
    print("🚩 RED FLAG: Tested many biomarkers")
    print("   → High risk of false positives")
    print("   → Consider Bonferroni correction or validation")
    print()

# Check 2: Barely significant p-values with weak effects
weak_effects = biomarkers[(biomarkers['p_value'] < 0.05) &
                          (biomarkers['p_value'] > 0.01) &
                          (biomarkers['OR'] < 1.5)]
if len(weak_effects) > 0:
    red_flags.append("Weak effects with marginal significance")
    print("🚩 RED FLAG: Weak effects that barely reach significance")
    print(f"   → {len(weak_effects)} biomarker(s) with OR < 1.5 and p between 0.01-0.05")
    print("   → These may not replicate")
    print()

# Check 3: Very wide confidence intervals
wide_ci = biomarkers[biomarkers.apply(lambda x: x['CI_upper'] - x['CI_lower'] > 5, axis=1)]
if len(wide_ci) > 0:
    red_flags.append("Very wide confidence intervals")
    print("🚩 RED FLAG: Very uncertain estimates")
    print(f"   → {len(wide_ci)} biomarker(s) with very wide CI")
    print("   → Need more data for reliable estimates")
    print()

# Check 4: Perfect or near-perfect separation
perfect = biomarkers[biomarkers['AUC'] > 0.95]
if len(perfect) > 0:
    red_flags.append("Suspiciously high AUC")
    print("🚩 RED FLAG: Suspiciously high AUC (> 0.95)")
    print(f"   → {len(perfect)} biomarker(s) with AUC > 0.95")
    print("   → May indicate:")
    print("     - Overfitting")
    print("     - Data leakage")
    print("     - Technical artifact")
    print("   → Verify data quality")
    print()

if not red_flags:
    print("✓ No major red flags detected!")
    print("  Your results appear trustworthy")
else:
    print(f"⚠️  Found {len(red_flags)} potential issues")
    print("  → Interpret results with caution")
    print("  → Consider validation study")

print()
input("Press Enter to continue...")
print()

# ==============================================================================
# PART 7: Communicating to Non-Statisticians
# ==============================================================================
print("PART 7: Communicating to Non-Statisticians")
print("=" * 80)
print()

print("How to Explain Your Results to Clinical Team:")
print("-" * 80)
print()

best = biomarkers.iloc[0]

print("Instead of saying:")
print(f"  ❌ '{best['biomarker']} has OR={best['OR']:.2f}, 95% CI [{best['CI_lower']:.2f}-{best['CI_upper']:.2f}], p<0.001'")
print()

print("Say this:")
print(f"  ✓ 'Patients with high {best['biomarker']} are much more likely to respond.'")
print(f"  ✓ 'We're very confident this is a real effect, not random chance.'")
print(f"  ✓ 'This biomarker can predict who will respond with {best['AUC']:.0%} accuracy.'")
print()

print("For the enrichment strategy:")
criteria = analyzer.suggest_criteria()
print()
print("Instead of saying:")
print("  ❌ 'Using optimal Youden cutoffs for continuous predictors...'")
print()
print("Say this:")
print("  ✓ 'If we enroll only patients with these biomarker levels:'")
for criterion in criteria.criteria:
    print(f"     • {criterion}")
print(f"  ✓ 'Response rate improves from {criteria.response_rate_unenriched*100:.0f}% to {criteria.response_rate_enriched*100:.0f}%'")
print(f"  ✓ 'That's {criteria.enrichment_factor:.1f} times better success rate'")
print(f"  ✓ 'About {criteria.eligible_fraction*100:.0f}% of patients would qualify'")
print()

print("Key Communication Principles:")
print("-" * 80)
print("  1. Use plain language, avoid jargon")
print("  2. Focus on practical impact, not statistical technicalities")
print("  3. Use percentages and comparisons")
print("  4. Acknowledge uncertainty honestly")
print("  5. Connect to clinical outcomes")
print()

input("Press Enter for summary checklist...")
print()

# ==============================================================================
# SUMMARY CHECKLIST
# ==============================================================================
print("=" * 80)
print("SUMMARY: Statistical Interpretation Checklist")
print("=" * 80)
print()

print("Before trusting a biomarker, verify:")
print()
print("  □ Sample size adequate (>50 patients per group)")
print("  □ P-value meaningful (p < 0.01 preferred, p < 0.05 minimum)")
print("  □ Confidence interval doesn't include 1.0")
print("  □ Confidence interval is reasonably narrow")
print("  □ AUC shows useful discrimination (≥ 0.65)")
print("  □ Effect size is clinically meaningful (OR > 1.5)")
print("  □ Result makes biological sense")
print("  □ Not a result of multiple testing without correction")
print()

print("Before implementing enrichment strategy, ensure:")
print()
print("  □ Top biomarkers validated in independent data (ideal)")
print("  □ Biomarker assay is validated and available")
print("  □ Eligible population is large enough for recruitment")
print("  □ Benefits outweigh screening costs")
print("  □ Regulatory strategy supports enrichment")
print("  □ Commercial opportunity remains attractive")
print()

print("Red flags that require caution:")
print()
print("  ⚠️  P-value barely significant (0.04 < p < 0.05)")
print("  ⚠️  Very wide confidence intervals")
print("  ⚠️  Weak effect size (OR < 1.5)")
print("  ⚠️  Perfect or near-perfect AUC (> 0.95)")
print("  ⚠️  Results conflict with biological knowledge")
print("  ⚠️  Small sample size (< 30 per group)")
print("  ⚠️  Many biomarkers tested without correction")
print()

print("=" * 80)
print()
print("TUTORIAL COMPLETE!")
print()
print("You now know:")
print("  ✓ How to interpret odds ratios correctly")
print("  ✓ What confidence intervals really mean")
print("  ✓ When to trust (and not trust) p-values")
print("  ✓ How to evaluate AUC for clinical utility")
print("  ✓ Red flags that indicate unreliable results")
print("  ✓ How to communicate statistics to clinicians")
print()
print("Next steps:")
print("  • Apply this knowledge to your own analyses")
print("  • Always validate findings when possible")
print("  • Consider biological plausibility")
print("  • Consult with senior statisticians on complex cases")
print()
print("=" * 80)
