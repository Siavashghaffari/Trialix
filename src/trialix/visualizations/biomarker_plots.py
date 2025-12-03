"""Biomarker distribution visualizations."""

from typing import List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from pathlib import Path
from trialix.utils.constants import PLOT_DPI, PLOT_FIGSIZE, PLOT_COLORS


class BiomarkerPlotter:
    """Create biomarker distribution plots."""

    def __init__(self, data: pd.DataFrame, outcome_col: str = "_outcome_binary"):
        """
        Initialize biomarker plotter.

        Args:
            data: DataFrame with patient data
            outcome_col: Name of binary outcome column
        """
        self.data = data
        self.outcome_col = outcome_col

    def plot_distributions(
        self,
        biomarkers: List[str],
        save_path: Optional[str] = None,
        show: bool = False
    ) -> plt.Figure:
        """
        Plot biomarker distributions for responders vs non-responders.

        Args:
            biomarkers: List of biomarker names to plot
            save_path: Path to save plot (optional)
            show: Whether to display plot

        Returns:
            Matplotlib figure
        """
        n_biomarkers = len(biomarkers)
        n_cols = min(2, n_biomarkers)
        n_rows = (n_biomarkers + n_cols - 1) // n_cols

        fig, axes = plt.subplots(
            n_rows, n_cols, figsize=(PLOT_FIGSIZE[0], PLOT_FIGSIZE[1] * n_rows / 2)
        )

        if n_biomarkers == 1:
            axes = [axes]
        elif n_rows > 1:
            axes = axes.ravel()

        for idx, biomarker in enumerate(biomarkers):
            ax = axes[idx]
            self._plot_single_biomarker(biomarker, ax)

        # Hide unused subplots
        for idx in range(n_biomarkers, len(axes)):
            axes[idx].set_visible(False)

        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches="tight")

        if show:
            plt.show()

        return fig

    def _plot_single_biomarker(self, biomarker: str, ax: plt.Axes) -> None:
        """Plot a single biomarker distribution."""
        # Prepare data
        plot_data = self.data[[biomarker, self.outcome_col]].copy()
        plot_data = plot_data.dropna()

        # Map outcome to labels
        plot_data["Response"] = plot_data[self.outcome_col].map(
            {1: "Responder", 0: "Non-Responder"}
        )

        # Create box plot
        sns.boxplot(
            data=plot_data,
            x="Response",
            y=biomarker,
            ax=ax,
            palette={
                "Responder": PLOT_COLORS["responder"],
                "Non-Responder": PLOT_COLORS["non_responder"],
            }
        )

        # Add violin plot overlay for density
        sns.violinplot(
            data=plot_data,
            x="Response",
            y=biomarker,
            ax=ax,
            palette={
                "Responder": PLOT_COLORS["responder"],
                "Non-Responder": PLOT_COLORS["non_responder"],
            },
            alpha=0.3,
            inner=None,
        )

        # Statistical annotation
        from scipy import stats

        responder_vals = plot_data[plot_data["Response"] == "Responder"][biomarker]
        non_responder_vals = plot_data[plot_data["Response"] == "Non-Responder"][biomarker]

        # Mann-Whitney U test
        statistic, p_value = stats.mannwhitneyu(
            responder_vals, non_responder_vals, alternative="two-sided"
        )

        # Format p-value
        if p_value < 0.001:
            p_text = "p < 0.001"
        else:
            p_text = f"p = {p_value:.3f}"

        # Add median values
        median_resp = responder_vals.median()
        median_non_resp = non_responder_vals.median()

        title = f"{biomarker.replace('_', ' ').title()}\n{p_text}"
        subtitle = f"Median: R={median_resp:.1f}, NR={median_non_resp:.1f}"

        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("")
        ax.set_ylabel(biomarker.replace("_", " ").title(), fontsize=10)
        ax.text(
            0.5,
            0.02,
            subtitle,
            transform=ax.transAxes,
            ha="center",
            fontsize=9,
            style="italic",
        )

        # Grid
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
