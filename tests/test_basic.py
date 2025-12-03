"""Basic integration tests for Trialix."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import os

from trialix import TrialEnrichment
from trialix.core.data_loader import DataLoader
from trialix.core.biomarker_analysis import BiomarkerAnalyzer
from trialix.core.cutoff_optimizer import CutoffOptimizer
from trialix.core.criteria_generator import CriteriaGenerator


@pytest.fixture
def sample_data():
    """Generate sample trial data for testing."""
    np.random.seed(42)
    n = 100

    data = pd.DataFrame({
        "patient_id": [f"PT{i:03d}" for i in range(n)],
        "outcome": np.random.choice(["responder", "non_responder"], n, p=[0.4, 0.6]),
        "age": np.random.normal(60, 10, n),
        "biomarker_1": np.random.exponential(10, n),
        "biomarker_2": np.random.normal(50, 20, n),
    })

    return data


@pytest.fixture
def sample_csv_file(sample_data, tmp_path):
    """Create a temporary CSV file with sample data."""
    csv_path = tmp_path / "test_data.csv"
    sample_data.to_csv(csv_path, index=False)
    return str(csv_path)


class TestDataLoader:
    """Test data loading and validation."""

    def test_load_valid_data(self, sample_csv_file):
        """Test loading valid CSV data."""
        loader = DataLoader(sample_csv_file, outcome_col="outcome")
        data, summary = loader.load()

        assert data is not None
        assert len(data) == 100
        assert summary.n_patients == 100
        assert summary.n_responders > 0
        assert summary.n_non_responders > 0

    def test_load_missing_file(self):
        """Test error handling for missing file."""
        loader = DataLoader("nonexistent.csv", outcome_col="outcome")

        with pytest.raises(ValueError, match="File not found"):
            loader.load()

    def test_load_missing_outcome_column(self, sample_csv_file):
        """Test error handling for missing outcome column."""
        loader = DataLoader(sample_csv_file, outcome_col="missing_column")

        with pytest.raises(ValueError, match="Missing required column"):
            loader.load()


class TestBiomarkerAnalyzer:
    """Test biomarker analysis."""

    def test_analyze_biomarkers(self, sample_data):
        """Test biomarker analysis."""
        loader = DataLoader.__new__(DataLoader)
        loader.data = sample_data
        loader.data["_outcome_binary"] = (sample_data["outcome"] == "responder").astype(int)

        analyzer = BiomarkerAnalyzer(loader.data)
        results = analyzer.analyze_biomarkers(
            ["age", "biomarker_1", "biomarker_2"],
            min_auc=0.5,
            top_n=3
        )

        assert isinstance(results, pd.DataFrame)
        assert len(results) <= 3
        assert "biomarker" in results.columns
        assert "OR" in results.columns
        assert "p_value" in results.columns
        assert "AUC" in results.columns


class TestTrialEnrichment:
    """Test end-to-end TrialEnrichment workflow."""

    def test_complete_workflow(self, sample_csv_file, tmp_path):
        """Test complete enrichment analysis workflow."""
        # Initialize
        analyzer = TrialEnrichment(data=sample_csv_file, outcome="outcome")

        # Load data
        summary = analyzer.load_data()
        assert summary.n_patients == 100

        # Find biomarkers
        biomarkers = analyzer.find_biomarkers(top_n=2, min_auc=0.5)
        assert len(biomarkers) > 0

        # Optimize cutoffs
        cutoffs = analyzer.optimize_cutoffs()
        assert len(cutoffs) > 0

        # Generate criteria
        criteria = analyzer.suggest_criteria()
        assert criteria is not None
        assert len(criteria.criteria) > 0
        assert criteria.response_rate_unenriched >= 0
        assert criteria.response_rate_enriched >= 0

        # Export results
        output_dir = tmp_path / "results"
        analyzer.export(output_dir=str(output_dir), format="csv")

        # Check output files exist
        assert (output_dir / "biomarker_rankings.csv").exists()
        assert (output_dir / "optimal_cutoffs.csv").exists()
        assert (output_dir / "recommended_criteria.txt").exists()

    def test_to_json(self, sample_csv_file):
        """Test JSON export."""
        analyzer = TrialEnrichment(data=sample_csv_file, outcome="outcome")
        analyzer.load_data()
        analyzer.find_biomarkers(top_n=2, min_auc=0.5)
        analyzer.optimize_cutoffs()
        analyzer.suggest_criteria()

        json_output = analyzer.to_json()
        assert isinstance(json_output, str)
        assert "biomarker_rankings" in json_output
        assert "enrichment_criteria" in json_output


def test_package_import():
    """Test that package can be imported."""
    import trialix
    assert hasattr(trialix, "TrialEnrichment")
    assert hasattr(trialix, "__version__")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
