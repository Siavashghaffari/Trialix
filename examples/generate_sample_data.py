"""Generate sample oncology trial dataset for Trialix examples."""

import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Number of patients
n_patients = 150

# Generate patient IDs
patient_ids = [f"PT{i+1:03d}" for i in range(n_patients)]

# Generate demographic data
ages = np.random.normal(58, 12, n_patients).clip(25, 85).astype(int)

# Generate biomarker data
# PD-L1 score (0-100%, predictive of response)
pdl1_responders = np.random.gamma(8, 8, int(n_patients * 0.38))
pdl1_non_responders = np.random.gamma(3, 6, int(n_patients * 0.62))
pdl1_scores = np.concatenate([pdl1_responders, pdl1_non_responders])
pdl1_scores = np.clip(pdl1_scores, 0, 100)
np.random.shuffle(pdl1_scores)

# Tumor Mutational Burden (TMB) - mutations/megabase (0-30, somewhat predictive)
tmb_responders = np.random.exponential(8, int(n_patients * 0.38))
tmb_non_responders = np.random.exponential(5, int(n_patients * 0.62))
tmb = np.concatenate([tmb_responders, tmb_non_responders])
tmb = np.clip(tmb, 0.5, 30)
np.random.shuffle(tmb)

# KRAS mutation status (categorical, weakly predictive)
kras_prob = 0.35
kras_mutation = np.random.choice(
    ["positive", "negative"],
    n_patients,
    p=[kras_prob, 1 - kras_prob]
)

# Performance status (ECOG 0-2, weakly predictive)
ecog_ps = np.random.choice([0, 1, 2], n_patients, p=[0.3, 0.5, 0.2])

# Generate outcomes based on biomarkers
# Response probability is influenced by biomarkers
response_prob = np.zeros(n_patients)

# PD-L1 influence (strongest predictor)
response_prob += (pdl1_scores / 100) * 0.5

# Age influence (older patients respond better in this synthetic dataset)
response_prob += ((ages - 45) / 40) * 0.2

# TMB influence
response_prob += (tmb / 30) * 0.15

# KRAS influence
response_prob[kras_mutation == "positive"] += 0.1

# ECOG influence (better PS = better response)
response_prob -= ecog_ps * 0.05

# Add noise
response_prob += np.random.normal(0, 0.15, n_patients)

# Clip to valid probability range
response_prob = np.clip(response_prob, 0, 1)

# Generate binary outcomes
outcomes = (np.random.random(n_patients) < response_prob).astype(int)
outcome_labels = ["responder" if x == 1 else "non_responder" for x in outcomes]

# Create DataFrame
df = pd.DataFrame({
    "patient_id": patient_ids,
    "outcome": outcome_labels,
    "age": ages,
    "pdl1_score": pdl1_scores.round(1),
    "tmb": tmb.round(1),
    "kras_mutation": kras_mutation,
    "ecog_ps": ecog_ps,
})

# Add some missing values to make it realistic
missing_indices = np.random.choice(n_patients, size=int(n_patients * 0.05), replace=False)
for idx in missing_indices:
    col = np.random.choice(["pdl1_score", "tmb", "kras_mutation"])
    df.loc[idx, col] = np.nan

# Save to CSV
output_path = "examples/oncology_trial.csv"
df.to_csv(output_path, index=False)

print(f"✅ Sample dataset generated: {output_path}")
print(f"   - Total patients: {n_patients}")
print(f"   - Responders: {outcomes.sum()} ({outcomes.mean()*100:.1f}%)")
print(f"   - Non-responders: {n_patients - outcomes.sum()} ({(1-outcomes.mean())*100:.1f}%)")
print(f"   - Biomarkers: {len(df.columns) - 2}")
print("\nPreview:")
print(df.head(10))
