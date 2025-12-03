"""Output formatting utilities."""

from typing import Dict, Any
import json


class OutputFormatter:
    """Format analysis results for display and export."""

    @staticmethod
    def format_odds_ratio(or_value: float, ci_lower: float, ci_upper: float) -> str:
        """Format odds ratio with confidence interval."""
        return f"{or_value:.2f} [95% CI: {ci_lower:.2f}-{ci_upper:.2f}]"

    @staticmethod
    def format_p_value(p_value: float) -> str:
        """Format p-value for display."""
        if p_value < 0.001:
            return "<0.001"
        elif p_value < 0.01:
            return f"{p_value:.3f}"
        else:
            return f"{p_value:.3f}"

    @staticmethod
    def format_percentage(value: float) -> str:
        """Format value as percentage."""
        return f"{value * 100:.1f}%"

    @staticmethod
    def format_auc(auc: float) -> str:
        """Format AUC value."""
        return f"{auc:.2f}"

    @staticmethod
    def get_significance_stars(p_value: float) -> str:
        """Get star rating based on p-value."""
        if p_value < 0.001:
            return "⭐⭐⭐"
        elif p_value < 0.01:
            return "⭐⭐"
        elif p_value < 0.05:
            return "⭐"
        else:
            return "-"

    @staticmethod
    def format_biomarker_table_row(biomarker_result: Dict[str, Any]) -> str:
        """Format a single biomarker result for table display."""
        name = biomarker_result["biomarker"]
        or_val = biomarker_result["OR"]
        ci_lower = biomarker_result["CI_lower"]
        ci_upper = biomarker_result["CI_upper"]
        p_value = biomarker_result["p_value"]
        auc = biomarker_result["AUC"]

        or_str = OutputFormatter.format_odds_ratio(or_val, ci_lower, ci_upper)
        p_str = OutputFormatter.format_p_value(p_value)
        auc_str = OutputFormatter.format_auc(auc)
        stars = OutputFormatter.get_significance_stars(p_value)

        return f"{name:20s} | {or_str:30s} | {p_str:8s} | {auc_str:5s} | {stars}"

    @staticmethod
    def format_enrichment_summary(summary: Dict[str, Any]) -> str:
        """Format enrichment summary for text output."""
        lines = [
            "=" * 70,
            "RECOMMENDED INCLUSION CRITERIA",
            "=" * 70,
            "",
        ]

        # Add criteria
        if "criteria" in summary and summary["criteria"]:
            lines.append("Suggested Enrollment Criteria:")
            for criterion in summary["criteria"]:
                lines.append(f"  ✓ {criterion}")
            lines.append("")

        # Add impact
        lines.extend(
            [
                "Impact Estimate:",
                "-" * 70,
            ]
        )

        if "response_rate_unenriched" in summary:
            rr_unrich = OutputFormatter.format_percentage(summary["response_rate_unenriched"])
            lines.append(f"  Unenriched Response Rate: {rr_unrich}")

        if "response_rate_enriched" in summary:
            rr_enrich = OutputFormatter.format_percentage(summary["response_rate_enriched"])
            diff = summary["response_rate_enriched"] - summary["response_rate_unenriched"]
            diff_str = f"+{diff*100:.1f}pp" if diff > 0 else f"{diff*100:.1f}pp"
            lines.append(f"  Enriched Response Rate: {rr_enrich} ({diff_str})")

        if "eligible_fraction" in summary:
            eligible = OutputFormatter.format_percentage(summary["eligible_fraction"])
            lines.append(f"  Eligible Population: {eligible} of screened patients")

        if "enrichment_factor" in summary:
            factor = summary["enrichment_factor"]
            lines.append(f"  Relative Enrichment: {factor:.2f}x response rate improvement")

        if "number_needed_to_screen" in summary:
            nns = summary["number_needed_to_screen"]
            lines.append(f"  Number Needed to Screen: {nns:.1f} patients per randomized")

        lines.append("=" * 70)

        return "\n".join(lines)

    @staticmethod
    def to_json(data: Dict[str, Any], pretty: bool = True) -> str:
        """Convert data to JSON string."""
        if pretty:
            return json.dumps(data, indent=2)
        return json.dumps(data)
