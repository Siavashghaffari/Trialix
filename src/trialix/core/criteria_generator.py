"""Generate enrollment criteria recommendations."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np


@dataclass
class EnrichmentCriteria:
    """Container for enrichment criteria and impact estimates."""

    criteria: List[str]
    biomarkers_used: List[str]
    cutoffs: Dict[str, float]
    response_rate_unenriched: float
    response_rate_enriched: float
    eligible_fraction: float
    enrichment_factor: float
    number_needed_to_screen: float
    n_eligible: int
    n_total: int

    def summary(self) -> str:
        """Generate human-readable summary of criteria."""
        from trialix.utils.formatters import OutputFormatter

        summary_dict = {
            "criteria": self.criteria,
            "response_rate_unenriched": self.response_rate_unenriched,
            "response_rate_enriched": self.response_rate_enriched,
            "eligible_fraction": self.eligible_fraction,
            "enrichment_factor": self.enrichment_factor,
            "number_needed_to_screen": self.number_needed_to_screen,
        }

        return OutputFormatter.format_enrichment_summary(summary_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export."""
        return {
            "criteria": self.criteria,
            "biomarkers_used": self.biomarkers_used,
            "cutoffs": self.cutoffs,
            "response_rate_unenriched": self.response_rate_unenriched,
            "response_rate_enriched": self.response_rate_enriched,
            "eligible_fraction": self.eligible_fraction,
            "enrichment_factor": self.enrichment_factor,
            "number_needed_to_screen": self.number_needed_to_screen,
            "n_eligible": self.n_eligible,
            "n_total": self.n_total,
        }


class CriteriaGenerator:
    """Generate enrollment criteria based on biomarker analysis."""

    def __init__(self, data: pd.DataFrame, outcome_col: str = "_outcome_binary"):
        """
        Initialize criteria generator.

        Args:
            data: DataFrame with patient data
            outcome_col: Name of binary outcome column
        """
        self.data = data
        self.outcome_col = outcome_col

    def generate_criteria(
        self,
        biomarker_results: pd.DataFrame,
        cutoff_results: pd.DataFrame,
        max_criteria: int = 3,
        min_eligible_fraction: float = 0.2,
    ) -> EnrichmentCriteria:
        """
        Generate enrollment criteria recommendations.

        Args:
            biomarker_results: DataFrame with biomarker analysis results
            cutoff_results: DataFrame with optimal cutoffs
            max_criteria: Maximum number of criteria to include
            min_eligible_fraction: Minimum fraction of eligible patients

        Returns:
            EnrichmentCriteria object with recommendations
        """
        if biomarker_results.empty:
            raise ValueError("No significant biomarkers found")

        # Select top biomarkers
        top_biomarkers = biomarker_results.head(max_criteria)

        # Build criteria list and cutoffs dict
        criteria_list = []
        biomarkers_used = []
        cutoffs_dict = {}

        for _, row in top_biomarkers.iterrows():
            biomarker = row["biomarker"]

            # Find corresponding cutoff
            cutoff_row = cutoff_results[cutoff_results["biomarker"] == biomarker]

            if not cutoff_row.empty:
                cutoff = cutoff_row.iloc[0]["cutoff"]
                criteria_list.append(self._format_criterion(biomarker, cutoff))
                biomarkers_used.append(biomarker)
                cutoffs_dict[biomarker] = cutoff

        # Calculate combined impact
        impact = self._calculate_combined_impact(cutoffs_dict)

        # Check if eligible fraction meets minimum
        if impact["eligible_fraction"] < min_eligible_fraction:
            # Reduce number of criteria
            if len(cutoffs_dict) > 1:
                # Try with fewer criteria
                cutoffs_dict_reduced = {
                    list(cutoffs_dict.keys())[0]: list(cutoffs_dict.values())[0]
                }
                impact = self._calculate_combined_impact(cutoffs_dict_reduced)

                # Update criteria list
                criteria_list = criteria_list[:1]
                biomarkers_used = biomarkers_used[:1]
                cutoffs_dict = cutoffs_dict_reduced

        return EnrichmentCriteria(
            criteria=criteria_list,
            biomarkers_used=biomarkers_used,
            cutoffs=cutoffs_dict,
            response_rate_unenriched=impact["response_rate_unenriched"],
            response_rate_enriched=impact["response_rate_enriched"],
            eligible_fraction=impact["eligible_fraction"],
            enrichment_factor=impact["enrichment_factor"],
            number_needed_to_screen=impact["number_needed_to_screen"],
            n_eligible=impact["n_eligible"],
            n_total=impact["n_total"],
        )

    def _format_criterion(self, biomarker: str, cutoff: float) -> str:
        """
        Format a single criterion as human-readable text.

        Args:
            biomarker: Biomarker name
            cutoff: Cutoff value

        Returns:
            Formatted criterion string
        """
        # Clean up biomarker name (replace underscores with spaces, title case)
        biomarker_clean = biomarker.replace("_", " ").title()

        # Format cutoff based on magnitude
        if abs(cutoff) >= 1:
            cutoff_str = f"{cutoff:.1f}"
        else:
            cutoff_str = f"{cutoff:.2f}"

        # Determine units if possible (common patterns)
        if "age" in biomarker.lower():
            units = "years"
        elif "score" in biomarker.lower() or "percent" in biomarker.lower():
            cutoff_str = f"{cutoff:.0f}%"
            units = ""
        else:
            units = ""

        criterion = f"{biomarker_clean} ≥ {cutoff_str}"
        if units:
            criterion += f" {units}"

        return criterion

    def _calculate_combined_impact(self, cutoffs: Dict[str, float]) -> Dict[str, Any]:
        """
        Calculate impact of applying multiple criteria simultaneously.

        Args:
            cutoffs: Dictionary mapping biomarker names to cutoff values

        Returns:
            Dictionary with impact metrics
        """
        # Start with all patients
        eligible_mask = pd.Series(True, index=self.data.index)

        # Apply each criterion (AND logic)
        for biomarker, cutoff in cutoffs.items():
            if biomarker in self.data.columns:
                biomarker_mask = self.data[biomarker] >= cutoff
                eligible_mask &= biomarker_mask

        # Remove patients with missing outcome
        valid_outcome_mask = self.data[self.outcome_col].notna()
        eligible_mask &= valid_outcome_mask

        # Calculate metrics
        n_total = valid_outcome_mask.sum()
        n_eligible = eligible_mask.sum()

        eligible_fraction = n_eligible / n_total if n_total > 0 else 0.0

        # Response rates
        response_rate_unenriched = (
            self.data.loc[valid_outcome_mask, self.outcome_col].mean()
        )

        if n_eligible > 0:
            response_rate_enriched = (
                self.data.loc[eligible_mask, self.outcome_col].mean()
            )
        else:
            response_rate_enriched = 0.0

        # Enrichment factor
        if response_rate_unenriched > 0:
            enrichment_factor = response_rate_enriched / response_rate_unenriched
        else:
            enrichment_factor = 1.0

        # Number needed to screen
        if eligible_fraction > 0:
            number_needed_to_screen = 1.0 / eligible_fraction
        else:
            number_needed_to_screen = float("inf")

        return {
            "response_rate_unenriched": response_rate_unenriched,
            "response_rate_enriched": response_rate_enriched,
            "eligible_fraction": eligible_fraction,
            "enrichment_factor": enrichment_factor,
            "number_needed_to_screen": number_needed_to_screen,
            "n_eligible": n_eligible,
            "n_total": n_total,
        }

    def predict_eligibility(
        self, new_data: pd.DataFrame, criteria: EnrichmentCriteria
    ) -> pd.Series:
        """
        Predict eligibility for new patients based on criteria.

        Args:
            new_data: DataFrame with new patient data
            criteria: EnrichmentCriteria object

        Returns:
            Boolean series indicating eligibility
        """
        eligible_mask = pd.Series(True, index=new_data.index)

        for biomarker, cutoff in criteria.cutoffs.items():
            if biomarker in new_data.columns:
                eligible_mask &= new_data[biomarker] >= cutoff
            else:
                raise ValueError(f"Biomarker '{biomarker}' not found in new data")

        return eligible_mask
