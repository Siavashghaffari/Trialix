"""Constants used throughout Trialix."""

# Minimum data requirements
MIN_PATIENTS = 50
MIN_RESPONDERS = 10
MIN_NON_RESPONDERS = 10

# Default analysis parameters
DEFAULT_MIN_AUC = 0.6
DEFAULT_TOP_N = 5
DEFAULT_OUTPUT_DIR = "./trialix_results"
DEFAULT_PLOT_DPI = 300

# Statistical thresholds
DEFAULT_ALPHA = 0.05
DEFAULT_CI_LEVEL = 0.95

# Outcome encoding
RESPONDER_VALUES = ["responder", "1", 1, True, "yes", "response"]
NON_RESPONDER_VALUES = ["non_responder", "0", 0, False, "no", "non-response"]

# Plot settings
PLOT_DPI = 300
PLOT_STYLE = "seaborn-v0_8-darkgrid"
PLOT_FIGSIZE = (12, 8)
PLOT_COLORS = {
    "responder": "#2ecc71",  # Green
    "non_responder": "#e74c3c",  # Red
    "roc_curve": "#3498db",  # Blue
    "enriched": "#2ecc71",  # Green
    "unenriched": "#95a5a6",  # Gray
}

# Output file names
BIOMARKER_RANKINGS_FILE = "biomarker_rankings.csv"
OPTIMAL_CUTOFFS_FILE = "optimal_cutoffs.csv"
ENRICHMENT_SUMMARY_FILE = "enrichment_summary.json"
CRITERIA_FILE = "recommended_criteria.txt"
PLOT_DIR = "plots"
