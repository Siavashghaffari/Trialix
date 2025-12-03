"""Optimize cutoff values for continuous biomarkers."""

from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from sklearn.metrics import roc_curve
from sklearn.linear_model import LogisticRegression


class CutoffOptimizer:
    """Optimize cutoff values using Youden's Index."""

    def __init__(self, data: pd.DataFrame, outcome_col: str = "_outcome_binary"):
        """
        Initialize cutoff optimizer.

        Args:
            data: DataFrame with patient data
            outcome_col: Name of binary outcome column
        """
        self.data = data
        self.outcome_col = outcome_col

    def optimize_cutoff(
        self,
        biomarker: str,
        method: str = "youden",
        min_sensitivity: Optional[float] = None,
        min_specificity: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Find optimal cutoff value for a continuous biomarker.

        Args:
            biomarker: Name of biomarker column
            method: Optimization method ('youden' supported in MVP)
            min_sensitivity: Minimum required sensitivity (optional)
            min_specificity: Minimum required specificity (optional)

        Returns:
            Dictionary with cutoff value and performance metrics
        """
        # Get valid data
        valid_idx = self.data[biomarker].notna() & self.data[self.outcome_col].notna()

        if valid_idx.sum() < 20:
            raise ValueError(f"Insufficient data for biomarker '{biomarker}'")

        X = self.data.loc[valid_idx, biomarker].values.reshape(-1, 1)
        y = self.data.loc[valid_idx, self.outcome_col].values

        # Fit logistic regression to get probabilities
        model = LogisticRegression(penalty=None, max_iter=1000)
        model.fit(X, y)
        y_pred_proba = model.predict_proba(X)[:, 1]

        # Calculate ROC curve
        fpr, tpr, thresholds = roc_curve(y, y_pred_proba)

        if method == "youden":
            # Youden's Index = Sensitivity + Specificity - 1
            youden_index = tpr - fpr
            optimal_idx = np.argmax(youden_index)

            # Apply constraints if specified
            if min_sensitivity is not None or min_specificity is not None:
                valid_mask = np.ones(len(thresholds), dtype=bool)

                if min_sensitivity is not None:
                    valid_mask &= tpr >= min_sensitivity

                if min_specificity is not None:
                    specificity = 1 - fpr
                    valid_mask &= specificity >= min_specificity

                if valid_mask.sum() > 0:
                    valid_youden = youden_index.copy()
                    valid_youden[~valid_mask] = -np.inf
                    optimal_idx = np.argmax(valid_youden)

            optimal_threshold_proba = thresholds[optimal_idx]
            sensitivity = tpr[optimal_idx]
            specificity = 1 - fpr[optimal_idx]
            youden_j = youden_index[optimal_idx]

            # Map probability threshold back to biomarker value
            # Find biomarker value closest to this probability
            optimal_cutoff = self._map_threshold_to_biomarker_value(
                X.ravel(), y_pred_proba, optimal_threshold_proba
            )

        else:
            raise ValueError(f"Unsupported optimization method: {method}")

        # Calculate response rates above and below cutoff
        above_cutoff = X.ravel() >= optimal_cutoff
        below_cutoff = X.ravel() < optimal_cutoff

        response_rate_above = y[above_cutoff].mean() if above_cutoff.sum() > 0 else 0.0
        response_rate_below = y[below_cutoff].mean() if below_cutoff.sum() > 0 else 0.0

        return {
            "biomarker": biomarker,
            "cutoff": optimal_cutoff,
            "sensitivity": sensitivity,
            "specificity": specificity,
            "youden_index": youden_j,
            "response_rate_above": response_rate_above,
            "response_rate_below": response_rate_below,
            "n_above": above_cutoff.sum(),
            "n_below": below_cutoff.sum(),
        }

    @staticmethod
    def _map_threshold_to_biomarker_value(
        biomarker_values: np.ndarray,
        predicted_probas: np.ndarray,
        target_proba: float
    ) -> float:
        """
        Map probability threshold to biomarker value.

        Args:
            biomarker_values: Array of biomarker values
            predicted_probas: Predicted probabilities
            target_proba: Target probability threshold

        Returns:
            Biomarker value corresponding to target probability
        """
        # Find biomarker value where predicted probability is closest to target
        closest_idx = np.argmin(np.abs(predicted_probas - target_proba))
        return biomarker_values[closest_idx]

    def optimize_multiple_cutoffs(
        self, biomarker_list: list, method: str = "youden"
    ) -> pd.DataFrame:
        """
        Optimize cutoffs for multiple biomarkers.

        Args:
            biomarker_list: List of biomarker names
            method: Optimization method

        Returns:
            DataFrame with optimal cutoffs for each biomarker
        """
        results = []

        for biomarker in biomarker_list:
            try:
                result = self.optimize_cutoff(biomarker, method=method)
                results.append(result)
            except Exception as e:
                print(f"Warning: Could not optimize cutoff for '{biomarker}': {str(e)}")
                continue

        return pd.DataFrame(results)

    def calculate_enrichment_impact(
        self, biomarker: str, cutoff: float
    ) -> Dict[str, float]:
        """
        Calculate the impact of applying a cutoff for enrichment.

        Args:
            biomarker: Name of biomarker
            cutoff: Cutoff value

        Returns:
            Dictionary with enrichment metrics
        """
        valid_idx = self.data[biomarker].notna() & self.data[self.outcome_col].notna()
        data_subset = self.data.loc[valid_idx]

        # Overall response rate (unenriched)
        overall_response_rate = data_subset[self.outcome_col].mean()

        # Enriched population (above cutoff)
        enriched_mask = data_subset[biomarker] >= cutoff
        enriched_response_rate = (
            data_subset.loc[enriched_mask, self.outcome_col].mean()
            if enriched_mask.sum() > 0
            else 0.0
        )

        # Eligible fraction
        eligible_fraction = enriched_mask.mean()

        # Enrichment factor
        if overall_response_rate > 0:
            enrichment_factor = enriched_response_rate / overall_response_rate
        else:
            enrichment_factor = 1.0

        # Number needed to screen
        if eligible_fraction > 0:
            number_needed_to_screen = 1.0 / eligible_fraction
        else:
            number_needed_to_screen = float("inf")

        return {
            "biomarker": biomarker,
            "cutoff": cutoff,
            "response_rate_unenriched": overall_response_rate,
            "response_rate_enriched": enriched_response_rate,
            "eligible_fraction": eligible_fraction,
            "enrichment_factor": enrichment_factor,
            "number_needed_to_screen": number_needed_to_screen,
        }
