# Trialix

**Clinical Trial Enrichment Analysis** - Optimize patient selection and identify predictive biomarkers from historical trial data.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 What is Trialix?

Trialix transforms historical clinical trial data into actionable enrollment criteria recommendations. In under 2 minutes, you can:

- 🔬 **Discover predictive biomarkers** that stratify responders vs non-responders
- 📊 **Optimize enrollment criteria** using statistical analysis and machine learning
- 📈 **Predict enrichment impact** on trial success rates and population size
- 📉 **Generate publication-quality visualizations** for protocol development

**Perfect for:** Biostatisticians, Clinical Development Teams, Regulatory Affairs, and Trial Designers

---

## ⚡ Quick Start

### Installation

```bash
pip install trialix
```

### 5-Minute Example

```python
from trialix import TrialEnrichment

# Load historical trial data
analyzer = TrialEnrichment(data="trial_data.csv", outcome="responder")
analyzer.load_data()

# Discover predictive biomarkers
biomarkers = analyzer.find_biomarkers(top_n=5)
print(biomarkers)
#    biomarker      OR    CI_lower  CI_upper  p_value   AUC
# 0  pdl1_score    3.20      1.80      5.70    0.000   0.78
# 1  age           1.05      1.01      1.09    0.012   0.64

# Generate enrollment criteria
criteria = analyzer.suggest_criteria()
print(criteria.summary())
# Recommended Inclusion Criteria:
#   • PD-L1 tumor proportion score ≥ 50%
#   • Age ≥ 55 years
#
# Impact: 58% response rate (vs 38% unenriched), 35% eligible population

# Generate all plots and export results
analyzer.plot_all(save_to="results/plots/")
analyzer.export(output_dir="results/")
```

### CLI Usage

```bash
# Analyze trial data from command line
trialix analyze --input trial_data.csv --outcome responder --output results/

# Validate data format
trialix validate --input trial_data.csv --outcome responder
```

---

## 📦 Features

### Core Capabilities

- ✅ **CSV Data Ingestion** - Load clinical trial data from CSV files
- ✅ **Biomarker Discovery** - Logistic regression with odds ratios, p-values, and AUC
- ✅ **Optimal Cutoff Identification** - Youden's Index for continuous biomarkers
- ✅ **Enrollment Criteria Generation** - Data-driven inclusion/exclusion recommendations
- ✅ **Enrichment Impact Analysis** - Predict response rates and population sizes
- ✅ **Visualizations** - Biomarker distributions, ROC curves, enrichment charts
- ✅ **CLI & Python API** - Flexible interfaces for different workflows

### What Trialix Does

**Input:** CSV file with patient data (outcome + biomarkers)

```csv
patient_id,outcome,age,pdl1_score,tmb,kras_mutation
PT001,responder,58,65,12.5,positive
PT002,non_responder,45,10,3.2,negative
PT003,responder,62,80,18.1,positive
...
```

**Output:**
1. **Biomarker Rankings** - Which biomarkers predict response (OR, p-values, AUC)
2. **Optimal Cutoffs** - Where to draw the line for continuous biomarkers
3. **Enrollment Criteria** - Actionable recommendations for protocol design
4. **Impact Estimates** - Expected response rates, eligible population size
5. **Visualizations** - 3 key plots for stakeholder presentations

---

## 📖 Documentation

### Data Requirements

#### Minimum Requirements
- **File Format:** CSV
- **Minimum Patients:** 50
- **Minimum Responders:** 10
- **Minimum Non-Responders:** 10

#### Required Columns
- `patient_id`: Unique identifier (string)
- `outcome`: Binary response variable
  - Supported values: `responder`/`non_responder`, `1`/`0`, `yes`/`no`

#### Optional Columns
- Continuous biomarkers: age, lab values, biomarker scores (numeric)
- Categorical biomarkers: mutation status, biomarker categories (string)

### Python API Reference

#### TrialEnrichment Class

```python
from trialix import TrialEnrichment

# Initialize
analyzer = TrialEnrichment(
    data="path/to/data.csv",
    outcome="outcome_column_name",
    patient_id="patient_id"  # default: "patient_id"
)

# Load and validate data
summary = analyzer.load_data()
print(f"Loaded {summary.n_patients} patients, {summary.n_responders} responders")

# Find predictive biomarkers
biomarkers = analyzer.find_biomarkers(
    biomarker_list=None,  # default: all continuous biomarkers
    top_n=5,              # default: 5
    min_auc=0.6           # default: 0.6
)

# Optimize cutoffs
cutoffs = analyzer.optimize_cutoffs(
    biomarker_list=None,  # default: use biomarkers from find_biomarkers()
    method="youden"       # default: "youden"
)

# Generate enrollment criteria
criteria = analyzer.suggest_criteria(
    max_criteria=3,                # default: 3
    min_eligible_fraction=0.2      # default: 0.2 (20%)
)

# Visualizations
analyzer.plot_biomarkers(biomarkers=None, save_to="biomarkers.png")
analyzer.plot_roc_curves(save_to="roc.png")
analyzer.plot_enrichment_impact(save_to="impact.png")
analyzer.plot_all(save_to="plots/")  # Generate all plots

# Export results
analyzer.export(output_dir="results/", format="csv")  # or "json" or "all"
analyzer.to_json()  # Get JSON string of all results
```

#### EnrichmentCriteria Object

```python
criteria = analyzer.suggest_criteria()

# Access attributes
criteria.criteria  # List of human-readable criteria
criteria.biomarkers_used  # List of biomarker names
criteria.cutoffs  # Dict mapping biomarkers to cutoff values
criteria.response_rate_unenriched  # Baseline response rate
criteria.response_rate_enriched  # Enriched response rate
criteria.eligible_fraction  # Fraction of patients eligible
criteria.enrichment_factor  # Fold improvement in response rate
criteria.number_needed_to_screen  # Patients to screen per randomized
criteria.n_eligible  # Number of eligible patients
criteria.n_total  # Total number of patients

# Methods
criteria.summary()  # Human-readable summary
criteria.to_dict()  # Dictionary for JSON export
```

### CLI Reference

#### `trialix analyze`

Perform complete enrichment analysis.

```bash
trialix analyze --input <file> --outcome <column> [OPTIONS]
```

**Options:**
- `--input, -i`: Path to CSV file (required)
- `--outcome, -o`: Name of outcome column (required)
- `--output, -d`: Output directory (default: `./trialix_results/`)
- `--top-n, -n`: Number of top biomarkers (default: `5`)
- `--min-auc, -a`: Minimum AUC threshold (default: `0.6`)
- `--format, -f`: Output format: `csv`, `json`, or `all` (default: `csv`)

**Example:**
```bash
trialix analyze \
  --input examples/oncology_trial.csv \
  --outcome outcome \
  --output my_results/ \
  --top-n 3 \
  --min-auc 0.65
```

#### `trialix validate`

Validate data format and quality.

```bash
trialix validate --input <file> --outcome <column>
```

**Example:**
```bash
trialix validate --input trial_data.csv --outcome responder
```

---

## 🧪 Examples

### Example 1: Oncology Trial with PD-L1 Biomarker

```python
from trialix import TrialEnrichment

# Analyze oncology trial data
analyzer = TrialEnrichment(
    data="examples/oncology_trial.csv",
    outcome="outcome"
)

# Load data
summary = analyzer.load_data()
print(f"Analyzing {summary.n_patients} patients...")

# Full analysis pipeline
biomarkers = analyzer.find_biomarkers(top_n=5, min_auc=0.6)
cutoffs = analyzer.optimize_cutoffs()
criteria = analyzer.suggest_criteria()

# Results
print("\n" + "="*70)
print(criteria.summary())
print("="*70)

# Export everything
analyzer.export(output_dir="oncology_results/", format="all")
analyzer.plot_all(save_to="oncology_results/plots/")
```

**Output:**
```
Analyzing 150 patients...

======================================================================
RECOMMENDED INCLUSION CRITERIA
======================================================================

Suggested Enrollment Criteria:
  ✓ Pdl1 Score ≥ 50.0%
  ✓ Age ≥ 55.0 years

Impact Estimate:
----------------------------------------------------------------------
  Unenriched Response Rate: 28.7%
  Enriched Response Rate: 48.5% (+19.8pp)
  Eligible Population: 34.7% of screened patients
  Relative Enrichment: 1.69x response rate improvement
  Number Needed to Screen: 2.9 patients per randomized
======================================================================
```

### Example 2: Jupyter Notebook Workflow

```python
# In Jupyter Notebook
%matplotlib inline

from trialix import TrialEnrichment
import pandas as pd

# Load and analyze
analyzer = TrialEnrichment(data="trial.csv", outcome="responder")
analyzer.load_data()

biomarkers = analyzer.find_biomarkers()

# Interactive exploration
biomarkers.style.background_gradient(subset=['AUC'], cmap='RdYlGn')

# Display plots inline
analyzer.plot_biomarkers(display=True)
analyzer.plot_roc_curves(display=True)
analyzer.plot_enrichment_impact(display=True)

# Export for protocol
criteria = analyzer.suggest_criteria()
with open("protocol_criteria.txt", "w") as f:
    f.write(criteria.summary())
```

---

## 🔬 How It Works

### Analysis Pipeline

1. **Data Loading & Validation**
   - Load CSV data
   - Validate required columns and sample size
   - Encode outcome variable
   - Identify continuous and categorical biomarkers

2. **Biomarker Discovery**
   - Univariate logistic regression for each biomarker
   - Calculate odds ratios (OR) with 95% confidence intervals
   - Compute p-values using Wald test
   - Calculate Area Under ROC Curve (AUC)
   - Rank biomarkers by statistical significance

3. **Cutoff Optimization**
   - Generate ROC curves for continuous biomarkers
   - Apply Youden's Index: J = Sensitivity + Specificity - 1
   - Find optimal cutoff value
   - Calculate response rates above/below cutoff

4. **Criteria Generation**
   - Select top predictive biomarkers
   - Combine criteria using AND logic
   - Calculate combined enrichment impact
   - Ensure minimum eligible population threshold

5. **Visualization & Export**
   - Generate biomarker distribution plots (box + violin plots)
   - Create ROC curves with AUC annotations
   - Plot enrichment impact (before/after comparison)
   - Export results to CSV, JSON, and text formats

### Statistical Methods

- **Logistic Regression:** Univariate analysis for odds ratios
- **Wald Test:** P-value calculation for coefficient significance
- **ROC Analysis:** Predictive performance assessment (AUC)
- **Youden's Index:** Optimal cutoff identification
- **Mann-Whitney U Test:** Biomarker distribution comparison

---

## 📊 Output Files

When you run `analyzer.export(output_dir="results/")`, Trialix creates:

```
results/
├── biomarker_rankings.csv       # Table of biomarkers with OR, p-values, AUC
├── optimal_cutoffs.csv          # Optimal cutoff values with sensitivity/specificity
├── enrichment_summary.json      # Machine-readable impact metrics
├── recommended_criteria.txt     # Human-readable protocol recommendations
└── plots/
    ├── biomarker_distributions.png  # Box/violin plots by response
    ├── roc_curves.png               # ROC curves for top biomarkers
    └── enrichment_impact.png        # Before/after enrichment comparison
```

---

## 🛠️ Development

### Local Installation

```bash
# Clone repository
git clone https://github.com/Siavashghaffari/Trialix.git
cd Trialix

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=trialix --cov-report=html

# Run specific test file
pytest tests/test_data_loader.py
```

### Code Quality

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

---

## 🤝 Contributing

We welcome contributions!

**How to contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## 🙏 Acknowledgments

- Inspired by the need for data-driven trial design in pharmaceutical R&D
- Built with industry-standard tools: pandas, scikit-learn, matplotlib
- Designed for biostatisticians and clinical development teams

---

## 🗺️ Roadmap

### v0.1.0 (Current - MVP)
- ✅ CSV data ingestion
- ✅ Binary outcome enrichment
- ✅ Logistic regression biomarker analysis
- ✅ Youden's Index cutoff optimization
- ✅ CLI and Python API
- ✅ Basic visualizations

### v0.2.0 (Planned)
- 🔮 Survival analysis (Cox regression, Kaplan-Meier)
- 🔮 Sample size calculations
- 🔮 CDISC SDTM/ADaM format support
- 🔮 Excel and SAS dataset input

### v0.3.0 (Future)
- 🔮 Advanced ML models (random forests, XGBoost)
- 🔮 Multivariate biomarker models
- 🔮 PDF/Word report generation
- 🔮 Interactive web dashboard

---

**Made with ❤️ for better clinical trials**
