"""Enrichment impact visualizations."""

from typing import Optional
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from trialix.core.criteria_generator import EnrichmentCriteria
from trialix.utils.constants import PLOT_DPI, PLOT_FIGSIZE, PLOT_COLORS


class EnrichmentPlotter:
    """Create enrichment impact plots."""

    @staticmethod
    def plot_enrichment_impact(
        criteria: EnrichmentCriteria,
        save_path: Optional[str] = None,
        show: bool = False
    ) -> plt.Figure:
        """
        Plot enrichment impact (before vs after).

        Args:
            criteria: EnrichmentCriteria object
            save_path: Path to save plot (optional)
            show: Whether to display plot

        Returns:
            Matplotlib figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=PLOT_FIGSIZE)

        # Plot 1: Response Rate Comparison
        categories = ["Unenriched\nPopulation", "Enriched\nPopulation"]
        response_rates = [
            criteria.response_rate_unenriched * 100,
            criteria.response_rate_enriched * 100,
        ]

        bars = ax1.bar(
            categories,
            response_rates,
            color=[PLOT_COLORS["unenriched"], PLOT_COLORS["enriched"]],
            edgecolor="black",
            linewidth=1.5,
        )

        # Add value labels on bars
        for bar, rate in zip(bars, response_rates):
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{rate:.1f}%",
                ha="center",
                va="bottom",
                fontsize=12,
                fontweight="bold",
            )

        # Add improvement annotation
        improvement = (
            criteria.response_rate_enriched - criteria.response_rate_unenriched
        ) * 100
        ax1.annotate(
            f"+{improvement:.1f}pp",
            xy=(1, criteria.response_rate_enriched * 100),
            xytext=(0.5, criteria.response_rate_enriched * 100 + 5),
            arrowprops=dict(arrowstyle="->", color="green", lw=2),
            fontsize=11,
            color="green",
            fontweight="bold",
        )

        ax1.set_ylabel("Response Rate (%)", fontsize=12, fontweight="bold")
        ax1.set_title("Response Rate Impact", fontsize=13, fontweight="bold")
        ax1.set_ylim(0, max(response_rates) * 1.3)
        ax1.grid(axis="y", alpha=0.3)
        ax1.set_axisbelow(True)

        # Plot 2: Population Size
        labels = ["All Patients", "Eligible\nPatients"]
        sizes = [criteria.n_total, criteria.n_eligible]
        fractions = [100, criteria.eligible_fraction * 100]

        bars2 = ax2.bar(
            labels,
            sizes,
            color=[PLOT_COLORS["unenriched"], PLOT_COLORS["enriched"]],
            edgecolor="black",
            linewidth=1.5,
        )

        # Add value labels
        for bar, size, frac in zip(bars2, sizes, fractions):
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{size}\n({frac:.0f}%)",
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold",
            )

        ax2.set_ylabel("Number of Patients", fontsize=12, fontweight="bold")
        ax2.set_title("Population Size", fontsize=13, fontweight="bold")
        ax2.set_ylim(0, max(sizes) * 1.3)
        ax2.grid(axis="y", alpha=0.3)
        ax2.set_axisbelow(True)

        # Overall title with enrichment metrics
        fig.suptitle(
            f"Enrichment Impact Analysis\n"
            f"Enrichment Factor: {criteria.enrichment_factor:.2f}x | "
            f"NNS: {criteria.number_needed_to_screen:.1f}",
            fontsize=15,
            fontweight="bold",
            y=1.0,
        )

        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches="tight")

        if show:
            plt.show()

        return fig

    @staticmethod
    def plot_waterfall(
        criteria: EnrichmentCriteria,
        save_path: Optional[str] = None,
        show: bool = False
    ) -> plt.Figure:
        """
        Create a waterfall chart showing step-by-step enrichment.

        Args:
            criteria: EnrichmentCriteria object
            save_path: Path to save plot (optional)
            show: Whether to display plot

        Returns:
            Matplotlib figure
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # Prepare data for waterfall
        base_rate = criteria.response_rate_unenriched * 100
        enriched_rate = criteria.response_rate_enriched * 100
        improvement = enriched_rate - base_rate

        # Create waterfall bars
        x_pos = [0, 1, 2]
        values = [base_rate, improvement, enriched_rate]
        labels = ["Baseline\nResponse", "Enrichment\nImprovement", "Final\nResponse"]
        colors = [PLOT_COLORS["unenriched"], "lightblue", PLOT_COLORS["enriched"]]

        # Plot bars
        bars = []
        cumulative = 0
        for i, (val, label, color) in enumerate(zip(values, labels, colors)):
            if i == 1:  # Improvement bar starts from baseline
                bar = ax.bar(i, val, bottom=base_rate, color=color, edgecolor="black", lw=1.5)
            else:
                bar = ax.bar(i, val, color=color, edgecolor="black", lw=1.5)
            bars.append(bar)

            # Add labels
            if i == 1:
                y_pos = base_rate + val / 2
            else:
                y_pos = val / 2

            ax.text(
                i,
                y_pos,
                f"{val:.1f}%",
                ha="center",
                va="center",
                fontsize=11,
                fontweight="bold",
            )

        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, fontsize=11)
        ax.set_ylabel("Response Rate (%)", fontsize=12, fontweight="bold")
        ax.set_title("Enrichment Waterfall Analysis", fontsize=14, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        ax.set_axisbelow(True)

        plt.tight_layout()

        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path, dpi=PLOT_DPI, bbox_inches="tight")

        if show:
            plt.show()

        return fig
