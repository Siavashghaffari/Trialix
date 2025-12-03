"""Biomarker analysis using logistic regression."""

from typing import List, Dict, Any
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from scipy import stats


class BiomarkerAnalyzer:
    """Analyze biomarkers for treatment response prediction."""

    def __init__(self, data: pd.DataFrame, outcome_col: str = "_outcome_binary"):
        """
        Initialize biomarker analyzer.

        Args:
            data: DataFrame with patient data
            outcome_col: Name of binary outcome column
        """
        self.data = data
        self.outcome_col = outcome_col
        self.results: List[Dict[str, Any]] = []

    def analyze_biomarkers(
        self,
        biomarker_list: List[str],
        min_auc: float = 0.6,
        top_n: int = 5
    ) -> pd.DataFrame:
        """
        Perform univariate logistic regression for each biomarker.

        Args:
            biomarker_list: List of biomarker column names
            min_auc: Minimum AUC threshold for significance
            top_n: Number of top biomarkers to return

        Returns:
            DataFrame with biomarker rankings
        """
        self.results = []

        for biomarker in biomarker_list:
            try:
                result = self._analyze_single_biomarker(biomarker)
                if result is not None:
                    self.results.append(result)
            except Exception as e:
                print(f"Warning: Could not analyze biomarker '{biomarker}': {str(e)}")
                continue

        # Convert to DataFrame and sort by p-value and AUC
        results_df = pd.DataFrame(self.results)

        if results_df.empty:
            return results_df

        # Sort by p-value (primary) and AUC (secondary)
        results_df = results_df.sort_values(["p_value", "AUC"], ascending=[True, False])

        # Filter by minimum AUC
        results_df = results_df[results_df["AUC"] >= min_auc]

        # Return top N
        return results_df.head(top_n).reset_index(drop=True)

    def _analyze_single_biomarker(self, biomarker: str) -> Dict[str, Any]:
        """
        Analyze a single biomarker using logistic regression.

        Args:
            biomarker: Name of biomarker column

        Returns:
            Dictionary with analysis results
        """
        # Get data for this biomarker
        valid_idx = self.data[biomarker].notna() & self.data[self.outcome_col].notna()

        if valid_idx.sum() < 20:  # Minimum sample size
            return None

        X = self.data.loc[valid_idx, [biomarker]].values
        y = self.data.loc[valid_idx, self.outcome_col].values

        # Check if biomarker is categorical (need to encode)
        if not pd.api.types.is_numeric_dtype(self.data[biomarker]):
            # One-hot encode categorical variable
            X_encoded = pd.get_dummies(X.ravel(), drop_first=True).values
            if X_encoded.shape[1] == 0:  # All same category
                return None
            X = X_encoded.reshape(-1, X_encoded.shape[1] if len(X_encoded.shape) > 1 else 1)

        # Fit logistic regression
        model = LogisticRegression(penalty=None, max_iter=1000)
        model.fit(X, y)

        # Calculate odds ratio
        coef = model.coef_[0][0]
        odds_ratio = np.exp(coef)

        # Calculate confidence interval for OR (Wald method)
        # Standard error of coefficient
        predictions = model.predict_proba(X)[:, 1]

        # Calculate p-value using Wald test
        # Standard error approximation
        se = self._calculate_standard_error(X, y, predictions)
        z_score = coef / se
        p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))

        # 95% CI for OR
        ci_lower = np.exp(coef - 1.96 * se)
        ci_upper = np.exp(coef + 1.96 * se)

        # Calculate AUC
        try:
            auc = roc_auc_score(y, predictions)
        except ValueError:
            auc = 0.5

        return {
            "biomarker": biomarker,
            "OR": odds_ratio,
            "CI_lower": ci_lower,
            "CI_upper": ci_upper,
            "p_value": p_value,
            "AUC": auc,
            "coefficient": coef,
        }

    @staticmethod
    def _calculate_standard_error(
        X: np.ndarray, y: np.ndarray, predictions: np.ndarray
    ) -> float:
        """
        Calculate standard error of logistic regression coefficient.

        Args:
            X: Feature matrix
            y: Target vector
            predictions: Predicted probabilities

        Returns:
            Standard error
        """
        # Variance of predictions
        variance = predictions * (1 - predictions)

        # Prevent division by zero
        variance = np.maximum(variance, 1e-10)

        # Information matrix (Fisher information)
        # For single coefficient: sum(p*(1-p)*x^2)
        if X.shape[1] == 1:
            info = np.sum(variance * (X ** 2))
        else:
            info = np.sum(variance[:, np.newaxis] * (X ** 2))

        # Standard error is 1/sqrt(information)
        if info > 0:
            se = 1.0 / np.sqrt(info)
        else:
            se = 1.0  # Fallback

        return se

    def analyze_categorical_biomarker(self, biomarker: str) -> Dict[str, Any]:
        """
        Analyze categorical biomarker by computing response rates per category.

        Args:
            biomarker: Name of categorical biomarker

        Returns:
            Dictionary with category-wise response rates
        """
        valid_idx = self.data[biomarker].notna() & self.data[self.outcome_col].notna()
        data_subset = self.data.loc[valid_idx]

        response_by_category = (
            data_subset.groupby(biomarker)[self.outcome_col]
            .agg(["mean", "count"])
            .to_dict("index")
        )

        return {
            "biomarker": biomarker,
            "type": "categorical",
            "response_by_category": response_by_category,
        }
