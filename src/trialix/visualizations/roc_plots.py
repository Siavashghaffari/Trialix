"""ROC curve visualizations."""

from typing import Optional
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc
from trialix.utils.constants import PLOT_DPI, PLOT_FIGSIZE, PLOT_COLORS


class ROCPlotter:
    """Create ROC curve plots."""

    def __init__(self, data: pd.DataFrame, outcome_col: str = "_outcome_binary"):
        """
        Initialize ROC plotter.

        Args:
            data: DataFrame with patient data
            outcome_col: Name of binary outcome column
        """
        self.data = data
        self.outcome_col = outcome_col

    def plot_roc_curves(
        self,
        biomarker_results: pd.DataFrame,
        save_path: Optional[str] = None,
        show: bool = False
    ) -> plt.Figure:
        """
        Plot ROC curves for top biomarkers.

        Args:
            biomarker_results: DataFrame with biomarker analysis results
            save_path: Path to save plot (optional)
            show: Whether to display plot

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=PLOT_FIGSIZE)

        # Plot ROC curve for each biomarker
        colors = plt.cm.Set2(np.linspace(0, 1, len(biomarker_results)))

        for idx, (_, row) in enumerate(biomarker_results.iterrows()):
            biomarker = row["biomarker"]
            auc_score = row["AUC"]

            fpr, tpr = self._calculate_roc(biomarker)

            if fpr is not None and tpr is not None:
                ax.plot(
                    fpr,
                    tpr,
                    color=colors[idx],
                    lw=2,
                    label=f"{biomarker} (AUC = {auc_score:.2f})",
                )

        # Plot diagonal (random classifier)
        ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random (AUC = 0.50)", alpha=0.5)

        # Formatting
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=12)
        ax.set_ylabel("True Positive Rate (Sensitivity)", fontsize=12)
        ax.set_title("ROC Curves - Top Predictive Biomarkers", fontsize=14, fontweight="bold")
        ax.legend(loc="lower right", fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_aspect("equal")

        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches="tight")

        if show:
            plt.show()

        return fig

    def _calculate_roc(self, biomarker: str) -> tuple:
        """Calculate ROC curve for a biomarker."""
        # Get valid data
        valid_idx = self.data[biomarker].notna() & self.data[self.outcome_col].notna()

        if valid_idx.sum() < 20:
            return None, None

        X = self.data.loc[valid_idx, biomarker].values.reshape(-1, 1)
        y = self.data.loc[valid_idx, self.outcome_col].values

        # Fit logistic regression
        model = LogisticRegression(penalty=None, max_iter=1000)
        model.fit(X, y)
        y_pred_proba = model.predict_proba(X)[:, 1]

        # Calculate ROC curve
        fpr, tpr, _ = roc_curve(y, y_pred_proba)

        return fpr, tpr
