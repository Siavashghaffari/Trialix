"""Quickstart example for Trialix."""

from trialix import TrialEnrichment

# Initialize analyzer with sample data
analyzer = TrialEnrichment(
    data="examples/oncology_trial.csv",
    outcome="outcome"
)

# Load and validate data
print("Loading data...")
summary = analyzer.load_data()
print(f"✓ Loaded {summary.n_patients} patients")
print(f"  - Responders: {summary.n_responders} ({summary.response_rate*100:.1f}%)")
print(f"  - Biomarkers: {len(summary.biomarkers)}")
print()

# Find predictive biomarkers
print("Finding biomarkers...")
biomarkers = analyzer.find_biomarkers(top_n=5, min_auc=0.6)
print(f"✓ Found {len(biomarkers)} significant biomarkers")
print("\nTop Biomarkers:")
print(biomarkers[["biomarker", "OR", "p_value", "AUC"]])
print()

# Optimize cutoffs
print("Optimizing cutoffs...")
cutoffs = analyzer.optimize_cutoffs()
print(f"✓ Optimized {len(cutoffs)} cutoff values")
print()

# Generate enrollment criteria
print("Generating enrollment criteria...")
criteria = analyzer.suggest_criteria()
print("✓ Criteria generated")
print()
print("="*70)
print(criteria.summary())
print("="*70)
print()

# Generate visualizations
print("Generating visualizations...")
analyzer.plot_all(save_to="examples/plots/", display=False)
print("✓ Plots saved to examples/plots/")
print()

# Export results
print("Exporting results...")
analyzer.export(output_dir="examples/results/", format="all")
print("✓ Results exported to examples/results/")
print()

print("🎉 Analysis complete!")
