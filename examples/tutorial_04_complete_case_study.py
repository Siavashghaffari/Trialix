"""
Tutorial 4: Complete Case Study - From Failed Trial to Success
===============================================================

In this tutorial, you'll work through a realistic scenario:

SCENARIO:
Your company just completed a Phase IIb trial that FAILED to meet its
primary endpoint. The board wants to know:
1. Should we abandon the program?
2. Or can we find a biomarker-enriched population that responds?

You have the Phase IIb data and need to:
- Analyze why the trial failed
- Identify subgroups that responded
- Design a Phase III enrichment strategy
- Present recommendations to leadership

This is a comprehensive, end-to-end case study combining all Trialix features.
"""

from trialix import TrialEnrichment
import pandas as pd
import time

def pause(message="Press Enter to continue..."):
    """Helper function for interactive pauses"""
    print()
    input(message)
    print()

print("=" * 80)
print("TUTORIAL 4: Complete Case Study - From Failed Trial to Success")
print("=" * 80)
print()

# ==============================================================================
# ACT 1: THE FAILED TRIAL
# ==============================================================================
print("ACT 1: THE FAILED TRIAL")
print("=" * 80)
print()

print("Date: Monday morning, 9:00 AM")
print("Location: Your office")
print()
print("Email from CEO:")
print("-" * 80)
print("""
Subject: URGENT - Phase IIb Results

Team,

The Phase IIb results came in over the weekend. Not good news.

Primary endpoint: 32% response rate (vs 40% target, p=0.08 vs placebo)
- Missed statistical significance
- Board meeting Friday to decide program fate

We invested $50M. Before we kill the program, I need to know:
Is there ANY patient population where this drug works?

I need your analysis by Thursday EOD.

Thanks,
Jane (CEO)
""")
print("-" * 80)
print()

print("Your mission: Save the program if possible")
print()

pause()

# ==============================================================================
# ACT 2: INITIAL DATA EXPLORATION
# ==============================================================================
print("ACT 2: INITIAL DATA EXPLORATION")
print("=" * 80)
print()

print("Step 1: Load the Phase IIb data")
print()

# Load data
data = pd.read_csv("examples/oncology_trial.csv")
print(f"✓ Loaded {len(data)} patients from Phase IIb")
print()

# Quick look at outcomes
outcome_summary = data['outcome'].value_counts()
total = len(data)
responders = outcome_summary.get('responder', 0)
response_rate = responders / total

print("Overall Results:")
print(f"  Response rate: {response_rate*100:.1f}%")
print(f"  Responders: {responders}")
print(f"  Non-responders: {total - responders}")
print()

if response_rate < 0.35:
    print("💔 Confirms failure - missed 40% target")
else:
    print("🤔 Close to target, might be salvageable")
print()

print("Step 2: What biomarkers do we have?")
biomarker_cols = [col for col in data.columns
                  if col not in ['patient_id', 'outcome']]
print(f"  Available biomarkers: {', '.join(biomarker_cols)}")
print()

pause()

# ==============================================================================
# ACT 3: THE SEARCH FOR RESPONDERS
# ==============================================================================
print("ACT 3: THE SEARCH FOR RESPONDERS")
print("=" * 80)
print()

print("Running comprehensive biomarker analysis...")
print()

# Initialize analyzer
analyzer = TrialEnrichment(
    data="examples/oncology_trial.csv",
    outcome="outcome"
)

# Load and analyze
summary = analyzer.load_data()

print("✓ Data validation passed")
print()

# Find ALL potential biomarkers (lower threshold for exploration)
biomarkers = analyzer.find_biomarkers(
    top_n=10,
    min_auc=0.55  # Lower threshold to not miss anything
)

print(f"Discovery: Found {len(biomarkers)} biomarkers with predictive signal")
print()

if len(biomarkers) == 0:
    print("😞 No predictive biomarkers found.")
    print("   Recommendation: TERMINATE program")
    print()
    print("END OF CASE STUDY")
    exit()

print("🎯 BREAKTHROUGH: We found predictive biomarkers!")
print()
print("Top Candidates:")
print("=" * 80)

# Show top 3
for idx, row in biomarkers.head(3).iterrows():
    print(f"\n{idx+1}. {row['biomarker'].upper()}")
    print(f"   Odds Ratio: {row['OR']:.2f} (Higher is better)")
    print(f"   P-value: {row['p_value']:.4f}")
    print(f"   AUC: {row['AUC']:.2f}")

    if row['AUC'] >= 0.70:
        print(f"   Assessment: ⭐ STRONG CANDIDATE")
    elif row['AUC'] >= 0.60:
        print(f"   Assessment: ✓ PROMISING")
    else:
        print(f"   Assessment: ⚠️  WEAK")

print()
print("=" * 80)
print()

best_biomarker = biomarkers.iloc[0]
print(f"💡 Key Finding: {best_biomarker['biomarker']} is highly predictive!")
print()

pause()

# ==============================================================================
# ACT 4: DEFINING THE ENRICHED POPULATION
# ==============================================================================
print("ACT 4: DEFINING THE ENRICHED POPULATION")
print("=" * 80)
print()

print("Question: If we select patients based on biomarkers,")
print("can we achieve the 40% response rate target?")
print()

# Optimize cutoffs
cutoffs = analyzer.optimize_cutoffs()

print("Optimal Cutoff Values:")
print("=" * 80)
for idx, row in cutoffs.head(3).iterrows():
    print(f"\n{row['biomarker']}: ≥ {row['cutoff']:.1f}")
    print(f"  Response rate above cutoff: {row['response_rate_above']*100:.1f}%")
    print(f"  Response rate below cutoff: {row['response_rate_below']*100:.1f}%")
    print(f"  Improvement: +{(row['response_rate_above']-row['response_rate_below'])*100:.1f} percentage points")

print()
print("=" * 80)
print()

# Generate criteria
print("Testing different enrichment strategies...")
print()

# Try different strategies
strategies = []

# Strategy 1: Single biomarker (most feasible)
criteria_single = analyzer.suggest_criteria(max_criteria=1, min_eligible_fraction=0.30)
strategies.append(('Single Biomarker', criteria_single))

# Strategy 2: Two biomarkers (balanced)
criteria_double = analyzer.suggest_criteria(max_criteria=2, min_eligible_fraction=0.25)
strategies.append(('Two Biomarkers', criteria_double))

# Strategy 3: Three biomarkers (aggressive)
criteria_triple = analyzer.suggest_criteria(max_criteria=3, min_eligible_fraction=0.20)
strategies.append(('Three Biomarkers', criteria_triple))

print("Enrichment Strategy Comparison:")
print("=" * 80)
print(f"{'Strategy':<20} {'Response Rate':<15} {'Eligible %':<12} {'Meets 40% Goal?'}")
print("-" * 80)

for name, criteria in strategies:
    response = criteria.response_rate_enriched * 100
    eligible = criteria.eligible_fraction * 100
    meets_goal = "✓ YES" if response >= 40 else "✗ NO"

    print(f"{name:<20} {response:>6.1f}%{'':<8} {eligible:>6.1f}%{'':<5} {meets_goal}")

print("=" * 80)
print()

# Select best strategy that meets goal
successful_strategies = [(name, criteria) for name, criteria in strategies
                         if criteria.response_rate_enriched >= 0.40]

if successful_strategies:
    # Pick the one with highest eligibility (most feasible)
    selected_name, selected_criteria = max(successful_strategies,
                                           key=lambda x: x[1].eligible_fraction)

    print(f"🎉 SUCCESS: '{selected_name}' strategy achieves 40% target!")
    print()
    print("Selected Strategy:")
    for criterion in selected_criteria.criteria:
        print(f"  ✓ {criterion}")
    print()
    print(f"Results:")
    print(f"  Response rate: {selected_criteria.response_rate_enriched*100:.1f}%")
    print(f"  Eligible patients: {selected_criteria.eligible_fraction*100:.1f}%")
    print(f"  Enrichment factor: {selected_criteria.enrichment_factor:.2f}x")
else:
    print("😞 No strategy achieves 40% target")
    print("   Program may not be salvageable")
    exit()

print()
pause()

# ==============================================================================
# ACT 5: PHASE III TRIAL DESIGN
# ==============================================================================
print("ACT 5: PHASE III TRIAL DESIGN")
print("=" * 80)
print()

print("Now let's design the Phase III trial...")
print()

criteria = selected_criteria

# Power calculation (simplified)
target_responders = 200  # For 80% power
target_power = 0.80

print("Phase III Requirements:")
print(f"  Target statistical power: {target_power*100:.0f}%")
print(f"  Responders needed: {target_responders}")
print()

# Calculate sample sizes
patients_to_randomize = target_responders / criteria.response_rate_enriched
patients_to_screen = patients_to_randomize / criteria.eligible_fraction

print("Sample Size Calculation:")
print(f"  Patients to randomize: {patients_to_randomize:.0f}")
print(f"  Patients to screen: {patients_to_screen:.0f}")
print(f"  Screen failures: {patients_to_screen - patients_to_randomize:.0f}")
print()

# Feasibility assessment
sites_needed = 50
patients_per_site_per_year = 20
max_duration_years = 2.0

total_capacity = sites_needed * patients_per_site_per_year * max_duration_years

print("Feasibility Check:")
print(f"  Available sites: {sites_needed}")
print(f"  Screening capacity: {patients_per_site_per_year} patients/site/year")
print(f"  Maximum duration: {max_duration_years} years")
print(f"  Total screening capacity: {total_capacity:.0f} patients")
print()

if patients_to_screen <= total_capacity:
    print(f"  ✓ FEASIBLE - Can screen {patients_to_screen:.0f} patients")
    enrollment_time = patients_to_screen / (sites_needed * patients_per_site_per_year)
    print(f"  Expected enrollment time: {enrollment_time:.1f} years")
else:
    print(f"  ⚠️  CHALLENGING - Need {patients_to_screen:.0f}, have capacity for {total_capacity:.0f}")
    print(f"  Options:")
    print(f"    - Add more sites")
    print(f"    - Extend timeline")
    print(f"    - Use less aggressive enrichment")

print()
pause()

# ==============================================================================
# ACT 6: COST-BENEFIT ANALYSIS
# ==============================================================================
print("ACT 6: COST-BENEFIT ANALYSIS")
print("=" * 80)
print()

print("Let's calculate the financial impact...")
print()

# Simplified cost model
cost_per_screened = 5000  # Screening + biomarker test
cost_per_randomized = 150000  # Full treatment cost
baseline_dev_cost = 50000000  # Already spent in Phase IIb

print("Cost Analysis:")
print()

# Unenriched (would need more patients for same power)
unenriched_randomize = target_responders / summary.response_rate
unenriched_total_cost = (unenriched_randomize * cost_per_randomized +
                         unenriched_randomize * cost_per_screened +  # Minimal screening
                         baseline_dev_cost)

print("Scenario 1: Continue without enrichment (not recommended - likely to fail)")
print(f"  Patients to randomize: {unenriched_randomize:.0f}")
print(f"  Phase III cost: ${(unenriched_total_cost - baseline_dev_cost)/1e6:.1f}M")
print(f"  Success probability: ~30% (based on Phase IIb failure)")
print(f"  Total program cost: ${unenriched_total_cost/1e6:.1f}M")
print()

# Enriched strategy
enriched_total_cost = (patients_to_screen * cost_per_screened +
                      patients_to_randomize * cost_per_randomized +
                      baseline_dev_cost)

print("Scenario 2: Enriched Phase III (recommended)")
print(f"  Patients to screen: {patients_to_screen:.0f}")
print(f"  Patients to randomize: {patients_to_randomize:.0f}")
print(f"  Phase III cost: ${(enriched_total_cost - baseline_dev_cost)/1e6:.1f}M")
print(f"  Success probability: ~70% (enriched for responders)")
print(f"  Total program cost: ${enriched_total_cost/1e6:.1f}M")
print()

# ROI calculation
market_size_enriched = 50000  # Patients/year eligible
revenue_per_patient = 100000
years_on_market = 10

total_revenue = market_size_enriched * revenue_per_patient * years_on_market
roi = (total_revenue - enriched_total_cost) / enriched_total_cost * 100

print("Return on Investment (if successful):")
print(f"  Target market size (enriched): {market_size_enriched:,} patients/year")
print(f"  Revenue per patient: ${revenue_per_patient:,}")
print(f"  10-year revenue: ${total_revenue/1e9:.1f}B")
print(f"  ROI: {roi:.0f}% return on investment")
print()

if roi > 200:
    print("  ✓ STRONG business case")
else:
    print("  ⚠️  Marginal business case")

print()
pause()

# ==============================================================================
# ACT 7: BOARD PRESENTATION
# ==============================================================================
print("ACT 7: BOARD PRESENTATION PREPARATION")
print("=" * 80)
print()

print("Generating visualizations and reports...")
print()

# Generate all outputs
analyzer.plot_all(save_to="examples/tutorial_04_board_presentation/plots/", display=False)
analyzer.export(output_dir="examples/tutorial_04_board_presentation/", format="all")

print("✓ Created presentation materials:")
print("  📊 Biomarker analysis charts")
print("  📊 ROC curves showing predictive power")
print("  📊 Enrichment impact visualization")
print("  📄 Statistical analysis summary")
print("  📄 Recommended inclusion criteria")
print()

pause()

# ==============================================================================
# ACT 8: THE RECOMMENDATION
# ==============================================================================
print("ACT 8: THE RECOMMENDATION")
print("=" * 80)
print()

print("=" * 80)
print("EXECUTIVE SUMMARY FOR BOARD")
print("=" * 80)
print()

print("QUESTION: Should we continue drug development?")
print()
print("ANSWER: YES - with biomarker enrichment strategy")
print()
print("=" * 80)
print()

print("KEY FINDINGS:")
print()
print("1. Phase IIb missed primary endpoint")
print(f"   - Overall response: {summary.response_rate*100:.1f}% (target: 40%)")
print("   - Statistical significance: NOT achieved")
print()

print("2. BUT: We identified responder subgroups")
print(f"   - {best_biomarker['biomarker']} strongly predicts response")
print(f"   - AUC = {best_biomarker['AUC']:.2f} (good predictive power)")
print(f"   - P-value < 0.001 (highly significant)")
print()

print("3. Enriched population achieves target")
print("   Recommended criteria:")
for criterion in criteria.criteria:
    print(f"   • {criterion}")
print(f"   → Response rate: {criteria.response_rate_enriched*100:.1f}% (exceeds 40% target)")
print(f"   → Eligible patients: {criteria.eligible_fraction*100:.1f}%")
print()

print("4. Phase III is feasible")
print(f"   - Need to screen {patients_to_screen:.0f} patients")
print(f"   - Achievable in {enrollment_time:.1f} years with {sites_needed} sites")
print(f"   - Phase III cost: ${(enriched_total_cost - baseline_dev_cost)/1e6:.1f}M")
print()

print("5. Strong commercial opportunity")
print(f"   - Market: {market_size_enriched:,} patients/year")
print(f"   - 10-year revenue: ${total_revenue/1e9:.1f}B")
print(f"   - ROI: {roi:.0f}%")
print()

print("=" * 80)
print()

print("RECOMMENDATION:")
print()
print("  ✓ Proceed to Phase III with enrichment")
print("  ✓ Require biomarker testing for enrollment")
print("  ✓ Target patient population defined by biomarkers")
print("  ✓ Success probability: ~70% (vs ~30% unenriched)")
print()

print("ALTERNATIVE:")
print()
print("  ✗ Terminate program")
print("    - Write off $50M investment")
print("    - Miss $5B+ market opportunity")
print()

print("=" * 80)
print()

pause("Press Enter for final thoughts...")

# ==============================================================================
# EPILOGUE
# ==============================================================================
print()
print("EPILOGUE: Six Months Later...")
print("=" * 80)
print()

print("The board approved the enriched Phase III trial.")
print()
print("What happened:")
print("  ✓ FDA accepted biomarker enrichment strategy")
print("  ✓ Companion diagnostic developed for biomarker testing")
print("  ✓ Phase III enrolled ahead of schedule")
print("  ✓ Data Safety Monitoring Board: positive interim results")
print("  ✓ Program value increased from $0 to $500M+")
print()

print("Your analysis saved:")
print("  • $50M invested capital")
print("  • 100+ jobs")
print("  • Potential blockbuster drug")
print("  • Future patients who will respond to treatment")
print()

print("=" * 80)
print()
print("TUTORIAL COMPLETE!")
print("=" * 80)
print()

print("What you learned:")
print("  ✓ How to rescue a failed trial")
print("  ✓ Finding responder subgroups")
print("  ✓ Designing enrichment strategies")
print("  ✓ Sample size and feasibility calculations")
print("  ✓ Cost-benefit analysis")
print("  ✓ Creating board presentations")
print("  ✓ Real-world decision making")
print()

print("Key lessons:")
print("  • A failed trial isn't always the end")
print("  • Biomarker enrichment can salvage programs")
print("  • Data-driven decisions beat gut instinct")
print("  • The right patients matter more than more patients")
print("  • Trialix can guide critical business decisions")
print()

print("This is why biomarker enrichment matters.")
print()
print("=" * 80)
