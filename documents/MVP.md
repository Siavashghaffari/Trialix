# Trialix MVP - Core Trial Enrichment Workflow

## The Magic Moment

**From historical trial data to predictive biomarkers and optimized enrollment criteria in under 2 minutes.**

User uploads a CSV with patient outcomes and biomarkers → Trialix identifies which biomarkers predict response → User gets actionable enrollment criteria to enrich their next trial.

---

## MVP Feature Set

### Single Focus: Binary Outcome Enrichment
Analyze one clinical trial dataset where patients are classified as **responders** or **non-responders**. Identify biomarkers that differentiate these groups and recommend enrollment criteria to enrich for likely responders.

---

## 1. Input Requirements

### 1.1 Data Format
**CSV file only** (Excel/CDISC deferred to v2)

### 1.2 Required Columns
```
patient_id,outcome,age,biomarker_1,biomarker_2,...,biomarker_N
PT001,responder,45,12.3,0.8,...,positive
PT002,non_responder,62,8.1,1.2,...,negative
...
```

**Mandatory:**
- `patient_id`: Unique patient identifier (string)
- `outcome`: Binary response variable (`responder` / `non_responder`, or `1` / `0`)

**Optional (biomarkers/demographics):**
- Continuous variables: age, BMI, lab values (numeric)
- Categorical variables: sex, biomarker status, mutation status (string/boolean)
- Column names are user-defined (no CDISC standards required)

### 1.3 Data Validation
- Minimum 50 patients (statistical power threshold)
- At least 10 responders and 10 non-responders (class balance check)
- Warning for missing values (simple imputation or row exclusion)

---

## 2. Core Analyses (Simple & Fast)

### 2.1 Biomarker Discovery
**Algorithm: Logistic Regression**
- Univariate logistic regression for each biomarker vs outcome
- Calculate odds ratios (OR) and 95% confidence intervals
- Rank biomarkers by p-value and effect size
- Identify top 5-10 most predictive biomarkers

**Output:**
```
Biomarker Rankings:
1. biomarker_PDL1    OR=3.2  [95% CI: 1.8-5.7]  p<0.001  ⭐⭐⭐
2. age               OR=1.05 [95% CI: 1.01-1.09] p=0.012  ⭐⭐
3. biomarker_KRAS    OR=2.1  [95% CI: 1.1-4.0]  p=0.024  ⭐⭐
...
```

### 2.2 Optimal Cutoff Identification
**For Continuous Biomarkers:**
- Use Youden's Index (maximize sensitivity + specificity) from ROC curve
- Calculate cutoff value (e.g., "age > 55" or "PDL1 > 50%")
- Report sensitivity, specificity, and predicted enrichment

**For Categorical Biomarkers:**
- Report response rate by category (e.g., "KRAS mutant: 45% response vs wild-type: 20%")

**Output:**
```
Optimal Cutoffs:
- biomarker_PDL1 ≥ 50%  → Response Rate: 65% (vs 28% below cutoff)
- age ≥ 55 years        → Response Rate: 52% (vs 35% below cutoff)
```

### 2.3 Enrollment Criteria Recommendations
**Simple Rule Generation:**
- Suggest inclusion criteria based on top biomarkers
- Estimate impact on trial population size and response rate
- Compare enriched vs unenriched populations

**Output:**
```
Recommended Inclusion Criteria:
✅ PDL1 expression ≥ 50% (tumor proportion score)
✅ Age ≥ 55 years

Impact Estimate:
- Eligible Population: 35% of screened patients (vs 100% unenriched)
- Expected Response Rate: 58% (vs 38% unenriched)
- Relative Enrichment: 1.5x response rate improvement
- Screen Failure Rate: ~65% (2.9 patients screened per randomized)
```

---

## 3. Visualizations (2-3 Key Plots)

### 3.1 Biomarker Distribution by Response
**Plot Type:** Box plots or violin plots
- Show biomarker distributions for responders vs non-responders
- Highlight statistically significant differences
- Generate for top 3-5 biomarkers

### 3.2 ROC Curves
**Plot Type:** Receiver Operating Characteristic curve
- Show predictive power of top biomarkers
- Display AUC (Area Under Curve) for each
- Mark optimal cutoff point (Youden's Index)

### 3.3 Enrichment Impact Chart
**Plot Type:** Bar chart or waterfall chart
- Compare response rates: unenriched vs enriched population
- Show trade-off: population size vs response rate improvement
- Visualize "before/after" enrichment scenario

**File Output:**
- Save plots as PNG (publication-quality, 300 DPI)
- Optional: Interactive HTML plots (plotly) for exploration

---

## 4. User Interfaces

### 4.1 Command-Line Interface (CLI)

**Basic Usage:**
```bash
trialix analyze --input trial_data.csv --outcome responder --output results/
```

**Parameters:**
- `--input` (required): Path to CSV file
- `--outcome` (required): Name of outcome column
- `--output` (optional): Output directory (default: `./trialix_results/`)
- `--min-auc` (optional): Minimum AUC threshold for biomarker selection (default: 0.6)
- `--top-n` (optional): Number of top biomarkers to report (default: 5)

**Output Structure:**
```
results/
├── biomarker_rankings.csv       # Table of all biomarkers with OR, p-values
├── recommended_criteria.txt     # Human-readable criteria suggestions
├── enrichment_summary.json      # Machine-readable results
├── plots/
│   ├── biomarker_distributions.png
│   ├── roc_curves.png
│   └── enrichment_impact.png
└── trialix_report.txt           # Full analysis log
```

**Progress Indicators:**
```
🔍 Loading data... ✓ (150 patients, 12 biomarkers)
📊 Analyzing biomarkers... ✓ (5 significant biomarkers found)
🎯 Optimizing cutoffs... ✓ (PDL1 ≥ 50%, age ≥ 55)
📈 Generating plots... ✓ (3 plots saved)
✅ Analysis complete! Results saved to: ./trialix_results/
```

### 4.2 Python API

**Simple Workflow:**
```python
from trialix import TrialEnrichment

# Load and analyze
analyzer = TrialEnrichment(data="trial_data.csv", outcome="responder")
analyzer.load_data()

# Find predictive biomarkers
biomarkers = analyzer.find_biomarkers(top_n=5, min_auc=0.6)
print(biomarkers)
# Output: DataFrame with [biomarker, OR, CI_lower, CI_upper, p_value, AUC]

# Get optimal cutoffs
cutoffs = analyzer.optimize_cutoffs()
print(cutoffs)
# Output: Dict like {"biomarker_PDL1": 50, "age": 55}

# Generate enrollment criteria
criteria = analyzer.suggest_criteria()
print(criteria.summary())
# Output: Text summary of recommended criteria + impact

# Generate visualizations
analyzer.plot_biomarkers(save_to="plots/")
analyzer.plot_roc_curves(save_to="plots/")
analyzer.plot_enrichment_impact(save_to="plots/")

# Export results
analyzer.export(output_dir="results/", format="csv")
```

**Jupyter Notebook Integration:**
- Display plots inline
- Return pandas DataFrames for custom analysis
- Interactive widgets (future: sliders to adjust cutoffs)

---

## 5. Technical Implementation (MVP)

### 5.1 Core Dependencies
```
pandas>=2.0.0          # Data handling
numpy>=1.24.0          # Numerical computation
scikit-learn>=1.3.0    # Logistic regression, ROC curves, metrics
matplotlib>=3.7.0      # Static plots
seaborn>=0.12.0        # Statistical visualizations
click>=8.1.0           # CLI framework
```

**Optional:**
```
plotly>=5.17.0         # Interactive plots (deferred to v1.1)
```

### 5.2 Project Structure
```
trialix/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── data_loader.py       # CSV ingestion and validation
│   ├── biomarker_analysis.py # Logistic regression, OR calculation
│   ├── cutoff_optimizer.py  # Youden's Index, ROC analysis
│   └── criteria_generator.py # Enrollment rule generation
├── visualizations/
│   ├── __init__.py
│   ├── biomarker_plots.py   # Box plots, violin plots
│   ├── roc_plots.py         # ROC curves
│   └── enrichment_plots.py  # Impact charts
├── cli/
│   ├── __init__.py
│   └── commands.py          # Click commands
├── api/
│   ├── __init__.py
│   └── enrichment.py        # TrialEnrichment class
└── utils/
    ├── __init__.py
    ├── validators.py        # Data validation
    └── formatters.py        # Output formatting
```

### 5.3 Key Algorithms (Simplified)

**Biomarker Ranking:**
```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

for biomarker in biomarker_columns:
    model = LogisticRegression()
    model.fit(X[[biomarker]], y)
    OR = np.exp(model.coef_[0][0])
    p_value = wald_test(model)  # scipy.stats
    AUC = roc_auc_score(y, model.predict_proba(X[[biomarker]])[:, 1])
    results.append({"biomarker": biomarker, "OR": OR, "p_value": p_value, "AUC": AUC})
```

**Cutoff Optimization:**
```python
from sklearn.metrics import roc_curve

fpr, tpr, thresholds = roc_curve(y, biomarker_values)
youden_index = tpr - fpr
optimal_idx = np.argmax(youden_index)
optimal_cutoff = thresholds[optimal_idx]
```

**Enrichment Impact:**
```python
# Unenriched population
response_rate_unenriched = y.mean()

# Enriched population (apply criteria)
enriched_mask = (data['biomarker_PDL1'] >= 50) & (data['age'] >= 55)
response_rate_enriched = y[enriched_mask].mean()
population_fraction = enriched_mask.mean()

enrichment_factor = response_rate_enriched / response_rate_unenriched
```

---

## 6. MVP Success Criteria

### 6.1 Functional Requirements
✅ Load CSV with 100-10,000 patient records in <5 seconds
✅ Complete biomarker analysis in <30 seconds for 20 biomarkers
✅ Generate all plots in <15 seconds
✅ **Total workflow time: <2 minutes** (data load → results export)
✅ Identify biomarkers with AUC ≥ 0.6 on test dataset
✅ Suggest ≥2 actionable inclusion criteria (if predictive biomarkers exist)

### 6.2 Usability Requirements
✅ First-time user completes example analysis in <5 minutes (with tutorial)
✅ CLI has clear error messages (e.g., "Missing 'outcome' column - expected column names: ...")
✅ Python API follows scikit-learn conventions (.fit(), .predict() patterns)
✅ Zero configuration required (sensible defaults)

### 6.3 Output Quality
✅ Biomarker rankings are reproducible (fixed random seed)
✅ Plots are publication-ready (labeled axes, legends, titles)
✅ Results include confidence intervals (no point estimates without uncertainty)

---

## 7. What's NOT in MVP (Deferred to Later)

### Deferred to v1.1+
❌ Survival analysis (Cox regression, Kaplan-Meier) - requires time-to-event data
❌ Sample size calculations - requires power analysis framework
❌ CDISC/SDTM parsing - requires domain knowledge and parsers (pyreadstat, xport)
❌ Multi-trial meta-analysis - requires trial normalization and weighting
❌ Advanced ML models (random forests, XGBoost) - adds complexity without clear MVP value
❌ Multivariate models (multiple biomarkers combined) - requires feature selection
❌ Subgroup discovery (clustering, decision trees) - complex to interpret
❌ PDF/Word report generation (python-docx, reportlab) - focus on programmatic output first
❌ Interactive dashboards (Plotly Dash, Streamlit) - web interface is v2.0
❌ Excel/SAS input - CSV is universal
❌ Missing data imputation (advanced) - simple exclusion for MVP
❌ Cross-validation and model selection - basic train/test split sufficient

### Why These Deferrals?
- **MVP goal**: Prove the core value proposition (biomarker discovery → criteria recommendations)
- **Speed to market**: Ship something useful in weeks, not months
- **User feedback**: Learn what users actually need before building advanced features
- **Technical debt**: Avoid premature optimization and over-engineering

---

## 8. Example Workflow (End-to-End)

### 8.1 Sample Dataset
**File: `oncology_trial.csv`**
```csv
patient_id,outcome,age,pdl1_score,tmb,kras_mutation
PT001,responder,58,65,12.5,positive
PT002,non_responder,45,10,3.2,negative
PT003,responder,62,80,18.1,positive
...
```

### 8.2 CLI Usage
```bash
$ trialix analyze --input oncology_trial.csv --outcome outcome --output results/

🔍 Loading data... ✓ (150 patients, 4 biomarkers)
   - Responders: 57 (38%)
   - Non-responders: 93 (62%)

📊 Analyzing biomarkers...
   ✓ pdl1_score: OR=3.2, p<0.001, AUC=0.78 ⭐⭐⭐
   ✓ age: OR=1.05, p=0.012, AUC=0.64 ⭐⭐
   ✓ tmb: OR=1.8, p=0.045, AUC=0.61 ⭐
   ✗ kras_mutation: OR=1.3, p=0.210, AUC=0.55 (not significant)

🎯 Optimizing cutoffs...
   ✓ pdl1_score ≥ 50% (sensitivity: 0.75, specificity: 0.68)
   ✓ age ≥ 55 years (sensitivity: 0.62, specificity: 0.58)

📈 Generating visualizations... ✓

✅ Analysis complete! Results saved to: ./results/

Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Recommended Inclusion Criteria:
  • PD-L1 tumor proportion score ≥ 50%
  • Age ≥ 55 years

Impact:
  • Enriched Response Rate: 58% (vs 38% unenriched)
  • Eligible Population: 35% of screened patients
  • Relative Improvement: 1.5x response rate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 8.3 Python API Usage
```python
from trialix import TrialEnrichment

# Quick analysis
analyzer = TrialEnrichment(data="oncology_trial.csv", outcome="outcome")
analyzer.load_data()

biomarkers = analyzer.find_biomarkers()
print(biomarkers.head(3))
# Output:
#    biomarker        OR  CI_lower  CI_upper  p_value   AUC
# 0  pdl1_score     3.20      1.80      5.70    0.000  0.78
# 1  age            1.05      1.01      1.09    0.012  0.64
# 2  tmb            1.80      1.02      3.18    0.045  0.61

criteria = analyzer.suggest_criteria()
print(criteria.summary())
# Output:
# Recommended Inclusion Criteria:
#   • PD-L1 tumor proportion score ≥ 50%
#   • Age ≥ 55 years
#
# Impact: 58% response rate (vs 38% unenriched), 35% eligible population

# Generate plots
analyzer.plot_all(save_to="results/plots/")
```

---

## 9. Testing & Validation

### 9.1 Unit Tests
- Data loader: Handle missing values, invalid formats, edge cases
- Logistic regression: Verify OR calculations match R/SAS
- ROC analysis: Validate Youden's Index against scikit-learn
- Criteria generator: Test enrichment calculations

### 9.2 Integration Tests
- End-to-end CLI workflow on sample dataset
- Python API workflow (load → analyze → export)
- Output file generation (CSV, PNG, JSON)

### 9.3 Validation Dataset
- Use public oncology trial data (e.g., TCGA, or synthetic dataset)
- Compare Trialix biomarker rankings to published results
- Validate OR/AUC calculations against R (glm, pROC packages)

---

## 10. Documentation (MVP)

### 10.1 README.md
- 30-second pitch ("What is Trialix?")
- Installation instructions (`pip install trialix`)
- Quickstart example (5 lines of code)
- Link to full documentation

### 10.2 Quickstart Tutorial
- Jupyter notebook: `examples/quickstart.ipynb`
- Sample dataset: `examples/oncology_trial.csv`
- Step-by-step walkthrough (15 minutes)

### 10.3 API Reference
- Docstrings for all public functions
- Parameter descriptions and examples
- Return value specifications

---

## 11. Distribution (MVP)

### 11.1 PyPI Package
```bash
pip install trialix
```

**Package metadata:**
- Name: `trialix`
- Version: `0.1.0` (MVP release)
- License: MIT (or Apache 2.0)
- Python: 3.9+
- Platforms: macOS, Linux, Windows

### 11.2 GitHub Repository
- Public repo: `github.com/[org]/trialix`
- CI/CD: GitHub Actions (pytest, linting, type checking)
- Issue tracker: Bug reports and feature requests
- Releases: Tagged versions with changelogs

---

## 12. MVP Development Timeline (Estimate)

**Agile Sprints (2-week sprints):**

**Sprint 1: Core Infrastructure**
- Project setup (repo, CI/CD, packaging)
- Data loader and validator
- Basic CLI skeleton

**Sprint 2: Biomarker Analysis**
- Logistic regression implementation
- OR calculation and ranking
- ROC curve generation

**Sprint 3: Criteria Generation & Visualization**
- Cutoff optimizer (Youden's Index)
- Criteria generator
- All 3 key plots

**Sprint 4: Polish & Documentation**
- Error handling and validation
- Quickstart tutorial and examples
- Testing and bug fixes
- PyPI release

**Total: ~8 weeks to MVP** (with 1-2 developers)

---

## 13. Success Metrics (Post-Launch)

### After 3 Months:
- 100+ PyPI downloads
- 3+ GitHub issues/discussions (user engagement)
- 1 case study (user applies Trialix to real trial)

### After 6 Months:
- 500+ downloads
- 10+ stars on GitHub
- 1 publication/blog post citing Trialix
- Feature requests guide v1.1 roadmap

---

## 14. The MVP Vision

**Core Philosophy:**
> "Make biomarker-driven trial enrichment accessible to every biostatistician, not just ML experts."

**The Magic:**
1. User uploads CSV from Excel/SAS export (5 seconds)
2. Runs `trialix analyze` (90 seconds)
3. Gets ranked biomarkers, optimal cutoffs, and enrollment criteria (immediately actionable)
4. Takes recommendations to clinical team meeting (same day)

**No PhD in statistics required. No custom code to write. Just data → insights → action.**

---

**Document Version**: 1.0 (MVP Scope)
**Last Updated**: 2025-12-03
**Status**: Ready for Development
