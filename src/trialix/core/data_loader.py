"""Data loading and validation module."""

from typing import Optional, Tuple
from dataclasses import dataclass
import pandas as pd
from trialix.utils.validators import DataValidator


@dataclass
class DataSummary:
    """Summary statistics for loaded data."""

    n_patients: int
    n_responders: int
    n_non_responders: int
    response_rate: float
    biomarkers: list
    continuous_biomarkers: list
    categorical_biomarkers: list


class DataLoader:
    """Load and validate clinical trial data."""

    def __init__(self, file_path: str, outcome_col: str, patient_id_col: str = "patient_id"):
        """
        Initialize data loader.

        Args:
            file_path: Path to CSV file
            outcome_col: Name of outcome column
            patient_id_col: Name of patient ID column (default: "patient_id")
        """
        self.file_path = file_path
        self.outcome_col = outcome_col
        self.patient_id_col = patient_id_col
        self.data: Optional[pd.DataFrame] = None
        self.summary: Optional[DataSummary] = None

    def load(self) -> Tuple[pd.DataFrame, DataSummary]:
        """
        Load and validate data from CSV file.

        Returns:
            Tuple of (dataframe, summary)

        Raises:
            ValueError: If data validation fails
        """
        # Load CSV
        try:
            self.data = pd.read_csv(self.file_path)
        except FileNotFoundError:
            raise ValueError(f"File not found: {self.file_path}")
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {str(e)}")

        # Validate data
        is_valid, errors = DataValidator.validate_dataframe(
            self.data, self.outcome_col, self.patient_id_col
        )

        if not is_valid:
            error_msg = "Data validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            raise ValueError(error_msg)

        # Encode outcome variable
        self.data["_outcome_binary"] = DataValidator.encode_outcome(self.data[self.outcome_col])

        # Generate summary
        self.summary = self._generate_summary()

        return self.data, self.summary

    def _generate_summary(self) -> DataSummary:
        """Generate summary statistics for the loaded data."""
        if self.data is None:
            raise RuntimeError("Data not loaded. Call load() first.")

        n_patients = len(self.data)
        n_responders = (self.data["_outcome_binary"] == 1).sum()
        n_non_responders = (self.data["_outcome_binary"] == 0).sum()
        response_rate = n_responders / n_patients

        # Identify biomarkers
        exclude_cols = [self.patient_id_col, self.outcome_col, "_outcome_binary"]
        biomarker_types = DataValidator.identify_biomarker_types(self.data, exclude_cols)

        all_biomarkers = (
            biomarker_types["continuous"] + biomarker_types["categorical"]
        )

        return DataSummary(
            n_patients=n_patients,
            n_responders=n_responders,
            n_non_responders=n_non_responders,
            response_rate=response_rate,
            biomarkers=all_biomarkers,
            continuous_biomarkers=biomarker_types["continuous"],
            categorical_biomarkers=biomarker_types["categorical"],
        )

    def get_biomarker_data(self, biomarker: str) -> pd.Series:
        """Get data for a specific biomarker."""
        if self.data is None:
            raise RuntimeError("Data not loaded. Call load() first.")

        if biomarker not in self.data.columns:
            raise ValueError(f"Biomarker '{biomarker}' not found in data")

        return self.data[biomarker].dropna()

    def get_outcome_data(self) -> pd.Series:
        """Get binary encoded outcome data."""
        if self.data is None:
            raise RuntimeError("Data not loaded. Call load() first.")

        return self.data["_outcome_binary"]
