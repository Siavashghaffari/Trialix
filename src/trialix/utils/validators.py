"""Data validation utilities."""

from typing import List, Tuple
import pandas as pd
import numpy as np
from trialix.utils.constants import (
    MIN_PATIENTS,
    MIN_RESPONDERS,
    MIN_NON_RESPONDERS,
    RESPONDER_VALUES,
    NON_RESPONDER_VALUES,
)


class DataValidator:
    """Validates clinical trial data for enrichment analysis."""

    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame, outcome_col: str, patient_id_col: str = "patient_id"
    ) -> Tuple[bool, List[str]]:
        """
        Validate that the dataframe meets requirements for analysis.

        Args:
            df: Input dataframe
            outcome_col: Name of outcome column
            patient_id_col: Name of patient ID column

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check if dataframe is empty
        if df.empty:
            errors.append("Dataframe is empty")
            return False, errors

        # Check for required columns
        if patient_id_col not in df.columns:
            errors.append(
                f"Missing required column '{patient_id_col}'. "
                f"Available columns: {', '.join(df.columns)}"
            )

        if outcome_col not in df.columns:
            available_cols = ", ".join(df.columns)
            suggestion = DataValidator._suggest_column(outcome_col, df.columns)
            error_msg = f"Missing required column '{outcome_col}'. Available columns: {available_cols}"
            if suggestion:
                error_msg += f". Did you mean '{suggestion}'?"
            errors.append(error_msg)
            return False, errors

        # Check minimum sample size
        n_patients = len(df)
        if n_patients < MIN_PATIENTS:
            errors.append(
                f"Insufficient sample size: {n_patients} patients "
                f"(minimum required: {MIN_PATIENTS})"
            )

        # Validate outcome column
        outcome_errors = DataValidator._validate_outcome_column(df, outcome_col)
        errors.extend(outcome_errors)

        # Check for biomarker columns (at least one column besides patient_id and outcome)
        biomarker_cols = [
            col for col in df.columns if col not in [patient_id_col, outcome_col]
        ]
        if len(biomarker_cols) == 0:
            errors.append("No biomarker columns found. At least one biomarker is required.")

        return len(errors) == 0, errors

    @staticmethod
    def _validate_outcome_column(df: pd.DataFrame, outcome_col: str) -> List[str]:
        """Validate the outcome column has proper values."""
        errors = []

        outcome_values = df[outcome_col].dropna().unique()

        # Check if binary
        if len(outcome_values) > 2:
            errors.append(
                f"Outcome column '{outcome_col}' has {len(outcome_values)} unique values. "
                "Expected binary outcome (2 values)."
            )
            return errors

        if len(outcome_values) < 2:
            errors.append(
                f"Outcome column '{outcome_col}' has only {len(outcome_values)} unique value. "
                "Expected binary outcome (2 values)."
            )
            return errors

        # Count responders and non-responders
        outcome_series = df[outcome_col].dropna()
        responder_mask = outcome_series.isin(RESPONDER_VALUES)
        n_responders = responder_mask.sum()
        n_non_responders = (~responder_mask).sum()

        if n_responders < MIN_RESPONDERS:
            errors.append(
                f"Insufficient responders: {n_responders} (minimum required: {MIN_RESPONDERS})"
            )

        if n_non_responders < MIN_NON_RESPONDERS:
            errors.append(
                f"Insufficient non-responders: {n_non_responders} "
                f"(minimum required: {MIN_NON_RESPONDERS})"
            )

        return errors

    @staticmethod
    def _suggest_column(target: str, available: List[str]) -> str:
        """Suggest a similar column name if available."""
        target_lower = target.lower()
        for col in available:
            if target_lower in col.lower() or col.lower() in target_lower:
                return col
        return ""

    @staticmethod
    def encode_outcome(series: pd.Series) -> pd.Series:
        """
        Encode outcome variable as binary (1 for responder, 0 for non-responder).

        Args:
            series: Outcome series

        Returns:
            Binary encoded series
        """
        encoded = series.copy()

        # Convert to string for comparison
        encoded_str = encoded.astype(str).str.lower()

        # Encode responders as 1
        responder_mask = encoded_str.isin([str(v).lower() for v in RESPONDER_VALUES])
        encoded = responder_mask.astype(int)

        return encoded

    @staticmethod
    def identify_biomarker_types(df: pd.DataFrame, exclude_cols: List[str]) -> dict:
        """
        Identify continuous and categorical biomarkers.

        Args:
            df: Input dataframe
            exclude_cols: Columns to exclude (patient_id, outcome)

        Returns:
            Dictionary with 'continuous' and 'categorical' lists
        """
        biomarker_cols = [col for col in df.columns if col not in exclude_cols]

        continuous = []
        categorical = []

        for col in biomarker_cols:
            # Skip columns with all missing values
            if df[col].isna().all():
                continue

            # Determine if continuous or categorical
            if pd.api.types.is_numeric_dtype(df[col]):
                # If numeric and has more than 10 unique values, treat as continuous
                n_unique = df[col].nunique()
                if n_unique > 10:
                    continuous.append(col)
                else:
                    categorical.append(col)
            else:
                categorical.append(col)

        return {"continuous": continuous, "categorical": categorical}
