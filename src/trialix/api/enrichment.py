"""Main Python API for trial enrichment analysis."""

from typing import Optional, List
from pathlib import Path
import pandas as pd
import json

from trialix.core.data_loader import DataLoader, DataSummary
from trialix.core.biomarker_analysis import BiomarkerAnalyzer
from trialix.core.cutoff_optimizer import CutoffOptimizer
from trialix.core.criteria_generator import CriteriaGenerator, EnrichmentCriteria
from trialix.visualizations.biomarker_plots import BiomarkerPlotter
from trialix.visualizations.roc_plots import ROCPlotter
from trialix.visualizations.enrichment_plots import EnrichmentPlotter
from trialix.utils.constants import (
    DEFAULT_MIN_AUC,
    DEFAULT_TOP_N,
    DEFAULT_OUTPUT_DIR,
    BIOMARKER_RANKINGS_FILE,
    OPTIMAL_CUTOFFS_FILE,
    ENRICHMENT_SUMMARY_FILE,
    CRITERIA_FILE,
    PLOT_DIR,
)


class TrialEnrichment:
    """
    Main class for clinical trial enrichment analysis.

    This class provides a high-level API for analyzing historical trial data
    and generating optimized enrollment criteria.

    Example:
        >>> analyzer = TrialEnrichment(data="trial.csv", outcome="responder")
        >>> analyzer.load_data()
        >>> biomarkers = analyzer.find_biomarkers()
        >>> criteria = analyzer.suggest_criteria()
        >>> print(criteria.summary())
    """

    def __init__(
        self,
        data: str,
        outcome: str,
        patient_id: str = "patient_id"
    ):
        """
        Initialize trial enrichment analyzer.

        Args:
            data: Path to CSV file with trial data
            outcome: Name of outcome column (binary: responder/non-responder)
            patient_id: Name of patient ID column (default: "patient_id")
        """
        self.data_path = data
        self.outcome_col = outcome
        self.patient_id_col = patient_id

        # Components (initialized after loading)
        self.loader: Optional[DataLoader] = None
        self.data: Optional[pd.DataFrame] = None
        self.summary: Optional[DataSummary] = None
        self.biomarker_analyzer: Optional[BiomarkerAnalyzer] = None
        self.cutoff_optimizer: Optional[CutoffOptimizer] = None
        self.criteria_generator: Optional[CriteriaGenerator] = None

        # Results (populated during analysis)
        self.biomarker_results: Optional[pd.DataFrame] = None
        self.cutoff_results: Optional[pd.DataFrame] = None
        self.enrichment_criteria: Optional[EnrichmentCriteria] = None

    def load_data(self) -> DataSummary:
        """
        Load and validate trial data.

        Returns:
            DataSummary object with dataset statistics

        Raises:
            ValueError: If data validation fails
        """
        self.loader = DataLoader(
            self.data_path,
            self.outcome_col,
            self.patient_id_col
        )

        self.data, self.summary = self.loader.load()

        # Initialize analyzers
        self.biomarker_analyzer = BiomarkerAnalyzer(self.data)
        self.cutoff_optimizer = CutoffOptimizer(self.data)
        self.criteria_generator = CriteriaGenerator(self.data)

        return self.summary

    def find_biomarkers(
        self,
        biomarker_list: Optional[List[str]] = None,
        top_n: int = DEFAULT_TOP_N,
        min_auc: float = DEFAULT_MIN_AUC,
    ) -> pd.DataFrame:
        """
        Identify predictive biomarkers for treatment response.

        Args:
            biomarker_list: List of biomarkers to analyze (default: all)
            top_n: Number of top biomarkers to return
            min_auc: Minimum AUC threshold

        Returns:
            DataFrame with ranked biomarkers

        Raises:
            RuntimeError: If data not loaded
        """
        if self.data is None or self.biomarker_analyzer is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")

        # Use all continuous biomarkers if not specified
        if biomarker_list is None:
            biomarker_list = self.summary.continuous_biomarkers

        self.biomarker_results = self.biomarker_analyzer.analyze_biomarkers(
            biomarker_list,
            min_auc=min_auc,
            top_n=top_n
        )

        return self.biomarker_results

    def optimize_cutoffs(
        self,
        biomarker_list: Optional[List[str]] = None,
        method: str = "youden"
    ) -> pd.DataFrame:
        """
        Optimize cutoff values for continuous biomarkers.

        Args:
            biomarker_list: List of biomarkers (default: use top biomarkers from find_biomarkers)
            method: Optimization method ('youden' supported)

        Returns:
            DataFrame with optimal cutoffs

        Raises:
            RuntimeError: If biomarkers not analyzed
        """
        if self.data is None or self.cutoff_optimizer is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")

        # Use biomarkers from find_biomarkers if not specified
        if biomarker_list is None:
            if self.biomarker_results is None:
                raise RuntimeError(
                    "Biomarkers not analyzed. Call find_biomarkers() first."
                )
            biomarker_list = self.biomarker_results["biomarker"].tolist()

        self.cutoff_results = self.cutoff_optimizer.optimize_multiple_cutoffs(
            biomarker_list,
            method=method
        )

        return self.cutoff_results

    def suggest_criteria(
        self,
        max_criteria: int = 3,
        min_eligible_fraction: float = 0.2,
    ) -> EnrichmentCriteria:
        """
        Generate enrollment criteria recommendations.

        Args:
            max_criteria: Maximum number of criteria to include
            min_eligible_fraction: Minimum fraction of eligible patients

        Returns:
            EnrichmentCriteria object

        Raises:
            RuntimeError: If biomarkers or cutoffs not analyzed
        """
        if self.biomarker_results is None or self.cutoff_results is None:
            raise RuntimeError(
                "Analysis not complete. Call find_biomarkers() and optimize_cutoffs() first."
            )

        if self.criteria_generator is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")

        self.enrichment_criteria = self.criteria_generator.generate_criteria(
            self.biomarker_results,
            self.cutoff_results,
            max_criteria=max_criteria,
            min_eligible_fraction=min_eligible_fraction,
        )

        return self.enrichment_criteria

    def plot_biomarkers(
        self,
        biomarkers: Optional[List[str]] = None,
        save_to: Optional[str] = None,
        display: bool = False,
    ) -> None:
        """
        Plot biomarker distributions.

        Args:
            biomarkers: List of biomarkers to plot (default: top biomarkers)
            save_to: Path to save plot
            display: Whether to display plot
        """
        if self.data is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")

        if biomarkers is None:
            if self.biomarker_results is None:
                raise RuntimeError("Biomarkers not analyzed. Call find_biomarkers() first.")
            biomarkers = self.biomarker_results["biomarker"].tolist()

        plotter = BiomarkerPlotter(self.data)
        plotter.plot_distributions(biomarkers, save_path=save_to, show=display)

    def plot_roc_curves(
        self,
        save_to: Optional[str] = None,
        display: bool = False,
    ) -> None:
        """
        Plot ROC curves for top biomarkers.

        Args:
            save_to: Path to save plot
            display: Whether to display plot
        """
        if self.data is None or self.biomarker_results is None:
            raise RuntimeError("Biomarkers not analyzed. Call find_biomarkers() first.")

        plotter = ROCPlotter(self.data)
        plotter.plot_roc_curves(self.biomarker_results, save_path=save_to, show=display)

    def plot_enrichment_impact(
        self,
        save_to: Optional[str] = None,
        display: bool = False,
    ) -> None:
        """
        Plot enrichment impact.

        Args:
            save_to: Path to save plot
            display: Whether to display plot
        """
        if self.enrichment_criteria is None:
            raise RuntimeError("Criteria not generated. Call suggest_criteria() first.")

        EnrichmentPlotter.plot_enrichment_impact(
            self.enrichment_criteria,
            save_path=save_to,
            show=display
        )

    def plot_all(
        self,
        save_to: str = "./plots",
        display: bool = False,
    ) -> None:
        """
        Generate all plots.

        Args:
            save_to: Directory to save plots
            display: Whether to display plots
        """
        Path(save_to).mkdir(parents=True, exist_ok=True)

        self.plot_biomarkers(
            save_to=str(Path(save_to) / "biomarker_distributions.png"),
            display=display
        )

        self.plot_roc_curves(
            save_to=str(Path(save_to) / "roc_curves.png"),
            display=display
        )

        self.plot_enrichment_impact(
            save_to=str(Path(save_to) / "enrichment_impact.png"),
            display=display
        )

    def export(
        self,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        format: str = "csv"
    ) -> None:
        """
        Export analysis results.

        Args:
            output_dir: Output directory
            format: Export format ('csv', 'json', or 'all')
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Export biomarker rankings
        if self.biomarker_results is not None and format in ["csv", "all"]:
            self.biomarker_results.to_csv(
                output_path / BIOMARKER_RANKINGS_FILE,
                index=False
            )

        # Export optimal cutoffs
        if self.cutoff_results is not None and format in ["csv", "all"]:
            self.cutoff_results.to_csv(
                output_path / OPTIMAL_CUTOFFS_FILE,
                index=False
            )

        # Export enrichment summary
        if self.enrichment_criteria is not None:
            summary_dict = self.enrichment_criteria.to_dict()

            # Convert numpy types to Python native types for JSON serialization
            def convert_to_native(obj):
                import numpy as np
                if isinstance(obj, (np.integer, np.int64, np.int32)):
                    return int(obj)
                elif isinstance(obj, (np.floating, np.float64, np.float32)):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                elif isinstance(obj, dict):
                    return {k: convert_to_native(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_to_native(item) for item in obj]
                return obj

            summary_dict = convert_to_native(summary_dict)

            if format in ["json", "all"]:
                with open(output_path / ENRICHMENT_SUMMARY_FILE, "w") as f:
                    json.dump(summary_dict, f, indent=2)

            # Export human-readable criteria
            with open(output_path / CRITERIA_FILE, "w") as f:
                f.write(self.enrichment_criteria.summary())

        # Export plots
        plot_path = output_path / PLOT_DIR
        self.plot_all(save_to=str(plot_path), display=False)

    def to_json(self) -> str:
        """
        Export all results to JSON string.

        Returns:
            JSON string with all results
        """
        results = {}

        if self.summary is not None:
            results["data_summary"] = {
                "n_patients": self.summary.n_patients,
                "n_responders": self.summary.n_responders,
                "n_non_responders": self.summary.n_non_responders,
                "response_rate": self.summary.response_rate,
                "biomarkers": self.summary.biomarkers,
            }

        if self.biomarker_results is not None:
            results["biomarker_rankings"] = self.biomarker_results.to_dict("records")

        if self.cutoff_results is not None:
            results["optimal_cutoffs"] = self.cutoff_results.to_dict("records")

        if self.enrichment_criteria is not None:
            results["enrichment_criteria"] = self.enrichment_criteria.to_dict()

        # Convert numpy types to Python native types for JSON serialization
        def convert_to_native(obj):
            import numpy as np
            if isinstance(obj, (np.integer, np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_to_native(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_native(item) for item in obj]
            return obj

        results = convert_to_native(results)

        return json.dumps(results, indent=2)
