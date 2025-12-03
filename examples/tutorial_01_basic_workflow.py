"""
Tutorial 1: Basic Workflow - Your First Trial Enrichment Analysis
===================================================================

In this tutorial, you'll learn:
- How to load and validate clinical trial data
- How to identify predictive biomarkers
- How to optimize enrollment criteria
- How to interpret and export results

Scenario: You're a biostatistician working on a Phase II oncology trial.
You have historical data from 150 patients and want to identify biomarkers
that could enrich your next trial for better response rates.
"""

from trialix import TrialEnrichment
import pandas as pd

print("=" * 80)
print("TUTORIAL 1: Basic Workflow - Your First Trial Enrichment Analysis")
print("=" * 80)
print()

# ==============================================================================
# STEP 1: Understanding Your Data
# ==============================================================================
print("STEP 1: Understanding Your Data")
print("-" * 80)
print()

print("Let's first look at what data we have:")
data = pd.read_csv("examples/oncology_trial.csv")
print(f"\nDataset shape: {data.shape[0]} patients x {data.shape[1]} columns")
print("\nFirst few rows:")
print(data.head())

print("\nColumn types:")
print(data.dtypes)

print("\nOutcome distribution:")
print(data['outcome'].value_counts())
print()

input("Press Enter to continue to Step 2...")
print()

# ==============================================================================
# STEP 2: Load and Validate Data with Trialix
# ==============================================================================
print("STEP 2: Load and Validate Data with Trialix")
print("-" * 80)
print()

print("Now let's use Trialix to load and validate our data:")
print()

# Initialize the analyzer
analyzer = TrialEnrichment(
    data="examples/oncology_trial.csv",
    outcome="outcome",           # Column containing responder/non-responder
    patient_id="patient_id"      # Column with patient IDs
)

# Load and validate
summary = analyzer.load_data()

print("✓ Data validation passed!")
print()
print("Data Summary:")
print(f"  Total patients: {summary.n_patients}")
print(f"  Responders: {summary.n_responders} ({summary.response_rate*100:.1f}%)")
print(f"  Non-responders: {summary.n_non_responders} ({(1-summary.response_rate)*100:.1f}%)")
print(f"  Baseline response rate: {summary.response_rate*100:.1f}%")
print()
print(f"  Biomarkers detected: {len(summary.biomarkers)}")
print(f"  - Continuous: {summary.continuous_biomarkers}")
print(f"  - Categorical: {summary.categorical_biomarkers}")
print()

input("Press Enter to continue to Step 3...")
print()

# ==============================================================================
# STEP 3: Discover Predictive Biomarkers
# ==============================================================================
print("STEP 3: Discover Predictive Biomarkers")
print("-" * 80)
print()

print("Let's find which biomarkers predict treatment response:")
print()

# Find top biomarkers
biomarkers = analyzer.find_biomarkers(
    top_n=5,           # Return top 5 biomarkers
    min_auc=0.6        # Minimum AUC threshold for clinical relevance
)

print(f"Found {len(biomarkers)} significant biomarkers (AUC ≥ 0.6, p < 0.05)")
print()
print("Biomarker Rankings:")
print("=" * 80)
print(biomarkers.to_string(index=False))
print("=" * 80)
print()

# Interpret the results
print("What do these numbers mean?")
print("-" * 80)
for idx, row in biomarkers.iterrows():
    print(f"\n{idx + 1}. {row['biomarker'].upper()}")
    print(f"   Odds Ratio (OR): {row['OR']:.2f}")
    if row['OR'] > 1:
        print(f"   → Higher values INCREASE odds of response by {(row['OR']-1)*100:.0f}%")
    else:
        print(f"   → Higher values DECREASE odds of response")

    print(f"   95% CI: [{row['CI_lower']:.2f} - {row['CI_upper']:.2f}]")
    print(f"   → We're 95% confident the true OR is in this range")

    print(f"   p-value: {row['p_value']:.4f}")
    if row['p_value'] < 0.001:
        print(f"   → Extremely strong evidence (p < 0.001)")
    elif row['p_value'] < 0.01:
        print(f"   → Strong evidence (p < 0.01)")
    elif row['p_value'] < 0.05:
        print(f"   → Statistically significant (p < 0.05)")

    print(f"   AUC: {row['AUC']:.2f}")
    if row['AUC'] >= 0.8:
        print(f"   → Excellent predictive power")
    elif row['AUC'] >= 0.7:
        print(f"   → Good predictive power")
    elif row['AUC'] >= 0.6:
        print(f"   → Fair predictive power")

print()
input("Press Enter to continue to Step 4...")
print()

# ==============================================================================
# STEP 4: Optimize Cutoff Values
# ==============================================================================
print("STEP 4: Optimize Cutoff Values")
print("-" * 80)
print()

print("For continuous biomarkers, we need to find the optimal cutoff point.")
print("We'll use Youden's Index, which maximizes sensitivity + specificity.")
print()

# Optimize cutoffs
cutoffs = analyzer.optimize_cutoffs()

print("Optimal Cutoffs:")
print("=" * 80)
print(cutoffs.to_string(index=False))
print("=" * 80)
print()

# Interpret cutoffs
print("Understanding the cutoffs:")
print("-" * 80)
for idx, row in cutoffs.iterrows():
    print(f"\n{row['biomarker'].upper()} ≥ {row['cutoff']:.1f}")
    print(f"  Sensitivity: {row['sensitivity']:.2%} - catches {row['sensitivity']:.0%} of responders")
    print(f"  Specificity: {row['specificity']:.2%} - correctly excludes {row['specificity']:.0%} of non-responders")
    print(f"  Youden Index: {row['youden_index']:.2f} - overall performance score")

    print(f"\n  Response rates:")
    print(f"  - Above cutoff: {row['response_rate_above']*100:.1f}% ({row['n_above']} patients)")
    print(f"  - Below cutoff: {row['response_rate_below']*100:.1f}% ({row['n_below']} patients)")
    improvement = row['response_rate_above'] - row['response_rate_below']
    print(f"  - Improvement: +{improvement*100:.1f} percentage points")

print()
input("Press Enter to continue to Step 5...")
print()

# ==============================================================================
# STEP 5: Generate Enrollment Criteria
# ==============================================================================
print("STEP 5: Generate Enrollment Criteria")
print("-" * 80)
print()

print("Now let's combine the best biomarkers into enrollment criteria:")
print()

# Generate criteria
criteria = analyzer.suggest_criteria(
    max_criteria=3,                # Maximum 3 criteria (keep it simple)
    min_eligible_fraction=0.2      # At least 20% of patients should be eligible
)

print("=" * 80)
print(criteria.summary())
print("=" * 80)
print()

# Deep dive into the impact
print("Deep Dive: What Does This Mean for Your Trial?")
print("-" * 80)
print()

print(f"BASELINE (No Enrichment):")
print(f"  • Response rate: {criteria.response_rate_unenriched*100:.1f}%")
print(f"  • All patients eligible: {criteria.n_total}")
print(f"  • If you need 100 responders: Need to enroll ~{100/criteria.response_rate_unenriched:.0f} patients")
print()

print(f"WITH ENRICHMENT (Using recommended criteria):")
print(f"  • Response rate: {criteria.response_rate_enriched*100:.1f}% ↑")
print(f"  • Eligible patients: {criteria.n_eligible} ({criteria.eligible_fraction*100:.1f}%)")
print(f"  • If you need 100 responders: Need to enroll ~{100/criteria.response_rate_enriched:.0f} patients")
print()

print(f"TRIAL EFFICIENCY:")
print(f"  • Enrichment factor: {criteria.enrichment_factor:.2f}x improvement in response rate")
print(f"  • Screen failure rate: {(1-criteria.eligible_fraction)*100:.1f}%")
print(f"  • Patients to screen per randomized: {criteria.number_needed_to_screen:.1f}")
print()

# Calculate sample size implications
unenriched_n = 100 / criteria.response_rate_unenriched
enriched_n = 100 / criteria.response_rate_enriched
reduction = (unenriched_n - enriched_n) / unenriched_n * 100

print(f"SAMPLE SIZE IMPACT (for 100 responders):")
print(f"  • Without enrichment: {unenriched_n:.0f} patients")
print(f"  • With enrichment: {enriched_n:.0f} patients")
print(f"  • Reduction: {reduction:.0f}% fewer patients needed!")
print()

input("Press Enter to continue to Step 6...")
print()

# ==============================================================================
# STEP 6: Visualize Results
# ==============================================================================
print("STEP 6: Visualize Results")
print("-" * 80)
print()

print("Let's create visualizations to present to stakeholders:")
print()

# Generate all plots
analyzer.plot_all(save_to="examples/tutorial_01_plots/", display=False)

print("✓ Created 3 key visualizations:")
print("  1. biomarker_distributions.png - Shows how biomarkers differ between responders/non-responders")
print("  2. roc_curves.png - Shows predictive power of each biomarker")
print("  3. enrichment_impact.png - Shows before/after enrichment comparison")
print()
print("📁 Saved to: examples/tutorial_01_plots/")
print()

input("Press Enter to continue to Step 7...")
print()

# ==============================================================================
# STEP 7: Export Results
# ==============================================================================
print("STEP 7: Export Results")
print("-" * 80)
print()

print("Finally, let's export everything for your protocol and presentations:")
print()

# Export all results
analyzer.export(output_dir="examples/tutorial_01_results/", format="all")

print("✓ Exported results to: examples/tutorial_01_results/")
print()
print("Files created:")
print("  📄 biomarker_rankings.csv - Import into Excel for tables")
print("  📄 optimal_cutoffs.csv - Reference for protocol writing")
print("  📄 enrichment_summary.json - Machine-readable for further analysis")
print("  📄 recommended_criteria.txt - Copy-paste into protocol")
print("  📊 plots/ - All visualizations for presentations")
print()

# ==============================================================================
# STEP 8: Next Steps
# ==============================================================================
print("=" * 80)
print("TUTORIAL COMPLETE!")
print("=" * 80)
print()

print("What You've Learned:")
print("  ✓ How to load and validate trial data")
print("  ✓ How to identify predictive biomarkers")
print("  ✓ How to interpret odds ratios, p-values, and AUC")
print("  ✓ How to optimize biomarker cutoffs")
print("  ✓ How to generate enrollment criteria")
print("  ✓ How to assess trial efficiency improvements")
print("  ✓ How to visualize and export results")
print()

print("Next Steps:")
print("  1. Review the plots in examples/tutorial_01_plots/")
print("  2. Open recommended_criteria.txt for protocol language")
print("  3. Try Tutorial 2 for advanced workflows")
print("  4. Apply to your own trial data!")
print()

print("Questions to Consider:")
print("  • Is a screen failure rate of {:.0f}% feasible for your sites?".format(
    (1-criteria.eligible_fraction)*100))
print("  • Do the biomarker tests require fresh tissue or can use archival?")
print("  • What's the turnaround time for biomarker results?")
print("  • Should you use all criteria or just the strongest biomarker?")
print()

print("=" * 80)
