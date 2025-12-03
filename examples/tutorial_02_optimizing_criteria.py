"""
Tutorial 2: Optimizing Enrollment Criteria for Different Goals
===============================================================

In this tutorial, you'll learn:
- How to balance response rate vs. enrollment feasibility
- How to optimize for different trial objectives
- How to compare multiple enrichment strategies
- How to handle trade-offs in trial design

Scenario: You need to design a Phase III trial and must decide between:
1. Maximum enrichment (highest response rate, harder to enroll)
2. Moderate enrichment (balanced approach)
3. Minimal enrichment (easier enrollment, lower response rate)
"""

from trialix import TrialEnrichment
import pandas as pd

print("=" * 80)
print("TUTORIAL 2: Optimizing Enrollment Criteria for Different Goals")
print("=" * 80)
print()

# ==============================================================================
# SCENARIO SETUP
# ==============================================================================
print("SCENARIO: Phase III Trial Design Decision")
print("-" * 80)
print("""
You're planning a Phase III oncology trial:
- Need 200 responders for statistical power
- Budget allows screening up to 1000 patients
- Want to maximize success probability while maintaining feasibility

Question: How aggressive should your enrichment strategy be?
""")

input("Press Enter to start analysis...")
print()

# ==============================================================================
# STEP 1: Baseline Analysis
# ==============================================================================
print("STEP 1: Baseline Analysis - Understanding Your Data")
print("-" * 80)
print()

analyzer = TrialEnrichment(
    data="examples/oncology_trial.csv",
    outcome="outcome"
)

summary = analyzer.load_data()
print(f"Historical Data Summary:")
print(f"  Patients: {summary.n_patients}")
print(f"  Baseline response rate: {summary.response_rate*100:.1f}%")
print(f"  Available biomarkers: {', '.join(summary.continuous_biomarkers)}")
print()

# Find all significant biomarkers
biomarkers = analyzer.find_biomarkers(top_n=10, min_auc=0.55)
print(f"Identified {len(biomarkers)} predictive biomarkers")
print()

input("Press Enter to explore different strategies...")
print()

# ==============================================================================
# STEP 2: Strategy 1 - Maximum Enrichment
# ==============================================================================
print("STRATEGY 1: Maximum Enrichment (Highest Response Rate)")
print("=" * 80)
print()
print("Goal: Maximize response rate, even if enrollment is challenging")
print()

# Use top biomarkers with strict criteria
cutoffs_max = analyzer.optimize_cutoffs()
criteria_max = analyzer.suggest_criteria(
    max_criteria=3,               # Use multiple biomarkers
    min_eligible_fraction=0.15    # Accept lower eligibility (15%)
)

print("Recommended Criteria:")
for criterion in criteria_max.criteria:
    print(f"  ✓ {criterion}")
print()

print(f"Expected Outcomes:")
print(f"  Response rate: {criteria_max.response_rate_enriched*100:.1f}% (baseline: {criteria_max.response_rate_unenriched*100:.1f}%)")
print(f"  Enrichment factor: {criteria_max.enrichment_factor:.2f}x")
print(f"  Eligible patients: {criteria_max.eligible_fraction*100:.1f}%")
print(f"  Screen failure rate: {(1-criteria_max.eligible_fraction)*100:.1f}%")
print()

# Calculate feasibility
responders_needed = 200
patients_needed = responders_needed / criteria_max.response_rate_enriched
patients_to_screen = patients_needed / criteria_max.eligible_fraction

print(f"Trial Feasibility (for 200 responders):")
print(f"  Patients to randomize: {patients_needed:.0f}")
print(f"  Patients to screen: {patients_to_screen:.0f}")
print(f"  Screen failures: {patients_to_screen - patients_needed:.0f}")
print()

if patients_to_screen > 1000:
    print(f"⚠️  WARNING: Exceeds screening budget of 1000 patients!")
else:
    print(f"✓ Within screening budget of 1000 patients")
print()

input("Press Enter to see Strategy 2...")
print()

# ==============================================================================
# STEP 3: Strategy 2 - Moderate Enrichment
# ==============================================================================
print("STRATEGY 2: Moderate Enrichment (Balanced Approach)")
print("=" * 80)
print()
print("Goal: Balance response rate improvement with enrollment feasibility")
print()

# Use fewer biomarkers, less strict
criteria_moderate = analyzer.suggest_criteria(
    max_criteria=2,                # Fewer criteria
    min_eligible_fraction=0.30     # Higher eligibility (30%)
)

print("Recommended Criteria:")
for criterion in criteria_moderate.criteria:
    print(f"  ✓ {criterion}")
print()

print(f"Expected Outcomes:")
print(f"  Response rate: {criteria_moderate.response_rate_enriched*100:.1f}% (baseline: {criteria_moderate.response_rate_unenriched*100:.1f}%)")
print(f"  Enrichment factor: {criteria_moderate.enrichment_factor:.2f}x")
print(f"  Eligible patients: {criteria_moderate.eligible_fraction*100:.1f}%")
print(f"  Screen failure rate: {(1-criteria_moderate.eligible_fraction)*100:.1f}%")
print()

# Calculate feasibility
patients_needed_mod = responders_needed / criteria_moderate.response_rate_enriched
patients_to_screen_mod = patients_needed_mod / criteria_moderate.eligible_fraction

print(f"Trial Feasibility (for 200 responders):")
print(f"  Patients to randomize: {patients_needed_mod:.0f}")
print(f"  Patients to screen: {patients_to_screen_mod:.0f}")
print(f"  Screen failures: {patients_to_screen_mod - patients_needed_mod:.0f}")
print()

if patients_to_screen_mod > 1000:
    print(f"⚠️  WARNING: Exceeds screening budget of 1000 patients!")
else:
    print(f"✓ Within screening budget of 1000 patients")
print()

input("Press Enter to see Strategy 3...")
print()

# ==============================================================================
# STEP 4: Strategy 3 - Minimal Enrichment
# ==============================================================================
print("STRATEGY 3: Minimal Enrichment (Easiest Enrollment)")
print("=" * 80)
print()
print("Goal: Ensure easy enrollment while still getting some benefit")
print()

# Use only the strongest single biomarker
criteria_minimal = analyzer.suggest_criteria(
    max_criteria=1,                # Single criterion only
    min_eligible_fraction=0.45     # High eligibility (45%)
)

print("Recommended Criteria:")
for criterion in criteria_minimal.criteria:
    print(f"  ✓ {criterion}")
print()

print(f"Expected Outcomes:")
print(f"  Response rate: {criteria_minimal.response_rate_enriched*100:.1f}% (baseline: {criteria_minimal.response_rate_unenriched*100:.1f}%)")
print(f"  Enrichment factor: {criteria_minimal.enrichment_factor:.2f}x")
print(f"  Eligible patients: {criteria_minimal.eligible_fraction*100:.1f}%")
print(f"  Screen failure rate: {(1-criteria_minimal.eligible_fraction)*100:.1f}%")
print()

# Calculate feasibility
patients_needed_min = responders_needed / criteria_minimal.response_rate_enriched
patients_to_screen_min = patients_needed_min / criteria_minimal.eligible_fraction

print(f"Trial Feasibility (for 200 responders):")
print(f"  Patients to randomize: {patients_needed_min:.0f}")
print(f"  Patients to screen: {patients_to_screen_min:.0f}")
print(f"  Screen failures: {patients_to_screen_min - patients_needed_min:.0f}")
print()

if patients_to_screen_min > 1000:
    print(f"⚠️  WARNING: Exceeds screening budget of 1000 patients!")
else:
    print(f"✓ Within screening budget of 1000 patients")
print()

input("Press Enter to compare all strategies...")
print()

# ==============================================================================
# STEP 5: Side-by-Side Comparison
# ==============================================================================
print("STEP 5: Side-by-Side Comparison")
print("=" * 80)
print()

# Create comparison table
comparison = pd.DataFrame({
    'Strategy': ['Baseline (No Enrichment)', 'Maximum Enrichment', 'Moderate Enrichment', 'Minimal Enrichment'],
    'Criteria Count': [0, len(criteria_max.criteria), len(criteria_moderate.criteria), len(criteria_minimal.criteria)],
    'Response Rate': [
        f"{criteria_max.response_rate_unenriched*100:.1f}%",
        f"{criteria_max.response_rate_enriched*100:.1f}%",
        f"{criteria_moderate.response_rate_enriched*100:.1f}%",
        f"{criteria_minimal.response_rate_enriched*100:.1f}%"
    ],
    'Enrichment Factor': [
        "1.0x",
        f"{criteria_max.enrichment_factor:.2f}x",
        f"{criteria_moderate.enrichment_factor:.2f}x",
        f"{criteria_minimal.enrichment_factor:.2f}x"
    ],
    'Eligible %': [
        "100%",
        f"{criteria_max.eligible_fraction*100:.1f}%",
        f"{criteria_moderate.eligible_fraction*100:.1f}%",
        f"{criteria_minimal.eligible_fraction*100:.1f}%"
    ],
    'To Screen (for 200 responders)': [
        f"{200/criteria_max.response_rate_unenriched:.0f}",
        f"{patients_to_screen:.0f}",
        f"{patients_to_screen_mod:.0f}",
        f"{patients_to_screen_min:.0f}"
    ],
    'Within Budget?': [
        "✓" if 200/criteria_max.response_rate_unenriched <= 1000 else "✗",
        "✓" if patients_to_screen <= 1000 else "✗",
        "✓" if patients_to_screen_mod <= 1000 else "✗",
        "✓" if patients_to_screen_min <= 1000 else "✗"
    ]
})

print(comparison.to_string(index=False))
print()
print("=" * 80)
print()

input("Press Enter for decision framework...")
print()

# ==============================================================================
# STEP 6: Decision Framework
# ==============================================================================
print("STEP 6: Decision Framework - Which Strategy to Choose?")
print("=" * 80)
print()

print("Consider These Factors:")
print()

print("1. RECRUITMENT FEASIBILITY")
print("   - How many sites do you have?")
print("   - What's the patient population size?")
print("   - What's acceptable screen failure rate?")
print("   → Higher screen failures = need more sites/longer recruitment")
print()

print("2. REGULATORY CONSIDERATIONS")
print("   - FDA/EMA expectations for your indication")
print("   - Precedent trials in the space")
print("   - Approvability of enriched population")
print("   → Too narrow = regulatory pushback")
print()

print("3. COMMERCIAL OPPORTUNITY")
print("   - Market size with enrichment")
print("   - Biomarker testing infrastructure")
print("   - Pricing and reimbursement")
print("   → Too enriched = small market")
print()

print("4. COMPETITIVE LANDSCAPE")
print("   - What are competitors doing?")
print("   - Speed to market importance")
print("   - Differentiation strategy")
print("   → Faster enrollment may win the race")
print()

print("5. STATISTICAL POWER")
print("   - Higher response rate = fewer patients needed")
print("   - But: smaller eligible population")
print("   - Trade-off: power vs. feasibility")
print()

print("=" * 80)
print()

print("RECOMMENDATION FRAMEWORK:")
print()
print("Choose MAXIMUM ENRICHMENT if:")
print("  • You have a large patient population")
print("  • Biomarker testing is fast and accessible")
print("  • You need highest probability of success")
print("  • You're willing to invest in extensive screening")
print()

print("Choose MODERATE ENRICHMENT if:")
print("  • You need balance between efficacy and feasibility")
print("  • Recruitment timeline is constrained")
print("  • You want regulatory/commercial flexibility")
print("  • Standard of care has moderate response rate")
print()

print("Choose MINIMAL ENRICHMENT if:")
print("  • Patient population is limited")
print("  • Screening capacity is constrained")
print("  • You need broad market access")
print("  • Biomarker testing is complex/expensive")
print()

print("Choose NO ENRICHMENT if:")
print("  • No biomarkers show strong predictive value")
print("  • All-comers trial is competitive advantage")
print("  • Regulatory path requires broad population")
print()

input("Press Enter for real-world example...")
print()

# ==============================================================================
# STEP 7: Real-World Example
# ==============================================================================
print("STEP 7: Real-World Example - Making the Decision")
print("=" * 80)
print()

print("Your Situation:")
print("  • 50 sites available globally")
print("  • Each site can screen ~25 patients/year")
print("  • Total screening capacity: 1,250 patients/year")
print("  • Target timeline: 18 months enrollment")
print("  • Need 200 responders for 80% power")
print()

print("Analysis:")
screening_capacity = 1250 * 1.5  # 18 months

print(f"  Available screening slots: {screening_capacity:.0f}")
print()

print("  Strategy fit:")
print(f"    Maximum:  {patients_to_screen:.0f} needed → {'✓ FEASIBLE' if patients_to_screen <= screening_capacity else '✗ NOT FEASIBLE'}")
print(f"    Moderate: {patients_to_screen_mod:.0f} needed → {'✓ FEASIBLE' if patients_to_screen_mod <= screening_capacity else '✗ NOT FEASIBLE'}")
print(f"    Minimal:  {patients_to_screen_min:.0f} needed → {'✓ FEASIBLE' if patients_to_screen_min <= screening_capacity else '✗ NOT FEASIBLE'}")
print()

# Recommend based on feasibility
feasible_strategies = []
if patients_to_screen <= screening_capacity:
    feasible_strategies.append("Maximum")
if patients_to_screen_mod <= screening_capacity:
    feasible_strategies.append("Moderate")
if patients_to_screen_min <= screening_capacity:
    feasible_strategies.append("Minimal")

if feasible_strategies:
    print(f"✓ RECOMMENDATION: {feasible_strategies[0]} Enrichment Strategy")
    print()
    print(f"  Rationale:")
    print(f"    • Feasible within your screening capacity")
    print(f"    • Maximizes response rate improvement")
    print(f"    • Provides sufficient sample size buffer")
else:
    print(f"⚠️  WARNING: All enrichment strategies exceed capacity!")
    print(f"  Options:")
    print(f"    1. Add more sites")
    print(f"    2. Extend enrollment period")
    print(f"    3. Use less aggressive enrichment")
    print(f"    4. Consider all-comers trial")

print()
print("=" * 80)
print()

print("TUTORIAL COMPLETE!")
print()
print("Key Takeaways:")
print("  ✓ Enrichment is a spectrum, not binary")
print("  ✓ More enrichment ≠ always better")
print("  ✓ Balance response rate, feasibility, and commercial goals")
print("  ✓ Use data to quantify trade-offs")
print("  ✓ Consider the full trial ecosystem")
print()

print("Next Steps:")
print("  1. Run this analysis with your own data")
print("  2. Discuss trade-offs with clinical and commercial teams")
print("  3. Model different scenarios in sensitivity analysis")
print("  4. Try Tutorial 3 for interpretation guidance")
print()

print("=" * 80)
