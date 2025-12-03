"""CLI commands for Trialix."""

import click
import sys
from pathlib import Path
from trialix.api.enrichment import TrialEnrichment
from trialix.utils.constants import DEFAULT_MIN_AUC, DEFAULT_TOP_N, DEFAULT_OUTPUT_DIR
from trialix import __version__


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Trialix - Clinical Trial Enrichment Analysis

    Optimize patient selection and identify predictive biomarkers from historical trial data.
    """
    pass


@cli.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True),
    help="Path to CSV file with trial data",
)
@click.option(
    "--outcome",
    "-o",
    required=True,
    help="Name of outcome column (binary: responder/non-responder)",
)
@click.option(
    "--output",
    "-d",
    "output_dir",
    default=DEFAULT_OUTPUT_DIR,
    type=click.Path(),
    help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
)
@click.option(
    "--top-n",
    "-n",
    default=DEFAULT_TOP_N,
    type=int,
    help=f"Number of top biomarkers to report (default: {DEFAULT_TOP_N})",
)
@click.option(
    "--min-auc",
    "-a",
    default=DEFAULT_MIN_AUC,
    type=float,
    help=f"Minimum AUC threshold (default: {DEFAULT_MIN_AUC})",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    default="csv",
    type=click.Choice(["csv", "json", "all"]),
    help="Output format (default: csv)",
)
def analyze(input_file, outcome, output_dir, top_n, min_auc, output_format):
    """
    Analyze trial data and generate enrichment recommendations.

    Example:
        trialix analyze --input trial.csv --outcome responder
    """
    try:
        # Print header
        click.echo("╔" + "═" * 70 + "╗")
        click.echo("║" + " " * 24 + "TRIALIX v" + __version__ + " " * 25 + "║")
        click.echo("║" + " " * 16 + "Clinical Trial Enrichment Analysis" + " " * 19 + "║")
        click.echo("╚" + "═" * 70 + "╝")
        click.echo()

        # Step 1: Load data
        click.echo("🔍 Loading data from: " + click.style(input_file, fg="cyan", bold=True))
        analyzer = TrialEnrichment(data=input_file, outcome=outcome)

        try:
            summary = analyzer.load_data()
        except ValueError as e:
            click.echo(click.style("\n❌ Error: " + str(e), fg="red", bold=True))
            sys.exit(1)

        click.echo(click.style("✓ Data loaded successfully", fg="green"))
        click.echo(f"  ├─ Total patients: {summary.n_patients}")
        click.echo(
            f"  ├─ Responders: {summary.n_responders} "
            f"({summary.response_rate * 100:.1f}%)"
        )
        click.echo(
            f"  ├─ Non-responders: {summary.n_non_responders} "
            f"({(1 - summary.response_rate) * 100:.1f}%)"
        )
        click.echo(f"  └─ Biomarkers found: {len(summary.biomarkers)}")
        click.echo()
        click.echo("━" * 72)
        click.echo()

        # Step 2: Analyze biomarkers
        click.echo("📊 Analyzing biomarkers...")
        biomarkers = analyzer.find_biomarkers(top_n=top_n, min_auc=min_auc)

        if biomarkers.empty:
            click.echo(
                click.style(
                    "\n⚠️  No significant biomarkers found (AUC >= " + str(min_auc) + ")",
                    fg="yellow",
                    bold=True,
                )
            )
            sys.exit(0)

        click.echo()
        click.echo("   Biomarker Rankings:")
        click.echo(
            "   ┌────────────────────┬─────────┬──────────────────┬──────────┬───────┬──────┐"
        )
        click.echo(
            "   │ Biomarker          │ Odds    │ 95% CI           │ p-value  │ AUC   │ Rank │"
        )
        click.echo(
            "   │                    │ Ratio   │                  │          │       │      │"
        )
        click.echo(
            "   ├────────────────────┼─────────┼──────────────────┼──────────┼───────┼──────┤"
        )

        from trialix.utils.formatters import OutputFormatter

        for _, row in biomarkers.iterrows():
            name = row["biomarker"][:18]
            or_val = f"{row['OR']:.2f}"
            ci = f"[{row['CI_lower']:.2f} - {row['CI_upper']:.2f}]"
            p_val = OutputFormatter.format_p_value(row["p_value"])
            auc = f"{row['AUC']:.2f}"
            stars = OutputFormatter.get_significance_stars(row["p_value"])

            click.echo(
                f"   │ {name:18s} │  {or_val:5s}  │ {ci:16s} │ {p_val:8s} │ {auc:5s} │ {stars:4s} │"
            )

        click.echo(
            "   └────────────────────┴─────────┴──────────────────┴──────────┴───────┴──────┘"
        )
        click.echo()
        click.echo(
            click.style(
                f"   ✓ Found {len(biomarkers)} significant biomarkers (p < 0.05)",
                fg="green",
            )
        )
        click.echo()
        click.echo("━" * 72)
        click.echo()

        # Step 3: Optimize cutoffs
        click.echo("🎯 Optimizing cutoff values...")
        cutoffs = analyzer.optimize_cutoffs()

        click.echo()
        click.echo("   Optimal Cutoffs (Youden's Index):")
        click.echo(
            "   ┌────────────────────┬───────────┬──────────────┬──────────────┬──────────┐"
        )
        click.echo(
            "   │ Biomarker          │ Cutoff    │ Sensitivity  │ Specificity  │ Youden J │"
        )
        click.echo(
            "   ├────────────────────┼───────────┼──────────────┼──────────────┼──────────┤"
        )

        for _, row in cutoffs.iterrows():
            name = row["biomarker"][:18]
            cutoff_val = f"≥ {row['cutoff']:.1f}"
            sens = f"{row['sensitivity']:.2f}"
            spec = f"{row['specificity']:.2f}"
            youden = f"{row['youden_index']:.2f}"

            click.echo(
                f"   │ {name:18s} │ {cutoff_val:9s} │    {sens:5s}     │    {spec:5s}     │  {youden:5s}   │"
            )

        click.echo(
            "   └────────────────────┴───────────┴──────────────┴──────────────┴──────────┘"
        )
        click.echo()
        click.echo("━" * 72)
        click.echo()

        # Step 4: Generate criteria
        click.echo("📈 Calculating enrichment impact...")
        criteria = analyzer.suggest_criteria()

        click.echo()
        click.echo("   ╔" + "═" * 70 + "╗")
        click.echo("   ║" + " " * 15 + "RECOMMENDED INCLUSION CRITERIA" + " " * 25 + "║")
        click.echo("   ╚" + "═" * 70 + "╝")
        click.echo()
        click.echo("   Suggested Enrollment Criteria:")
        for criterion in criteria.criteria:
            click.echo(click.style(f"   ✓ {criterion}", fg="green", bold=True))

        click.echo()
        click.echo("   ┌─────────────────────────────────────────────────────────────────────┐")
        click.echo("   │" + " " * 25 + "ENRICHMENT IMPACT" + " " * 29 + "│")
        click.echo("   ├─────────────────────────────────────────────────────────────────────┤")
        click.echo("   │" + " " * 69 + "│")

        rr_unrich = criteria.response_rate_unenriched * 100
        rr_enrich = criteria.response_rate_enriched * 100
        diff = rr_enrich - rr_unrich

        click.echo(f"   │  Unenriched Population:" + " " * 46 + "│")
        click.echo(f"   │  ├─ Response Rate: {rr_unrich:.1f}%" + " " * 45 + "│")
        click.echo(f"   │  └─ Eligible Patients: 100% (all screened)" + " " * 26 + "│")
        click.echo("   │" + " " * 69 + "│")
        click.echo(f"   │  Enriched Population (with criteria):" + " " * 31 + "│")
        click.echo(f"   │  ├─ Response Rate: {rr_enrich:.1f}%  ↑ +{diff:.1f}pp" + " " * 31 + "│")

        eligible_pct = criteria.eligible_fraction * 100
        click.echo(
            f"   │  ├─ Eligible Patients: {eligible_pct:.1f}% of screened" + " " * 26 + "│"
        )

        factor = criteria.enrichment_factor
        click.echo(f"   │  ├─ Relative Improvement: {factor:.2f}x response rate" + " " * 22 + "│")

        nns = criteria.number_needed_to_screen
        click.echo(
            f"   │  └─ Number Needed to Screen: {nns:.1f} patients per randomized" + " " * 9 + "│"
        )

        click.echo("   │" + " " * 69 + "│")
        click.echo("   └─────────────────────────────────────────────────────────────────────┘")
        click.echo()
        click.echo("━" * 72)
        click.echo()

        # Step 5: Generate visualizations
        click.echo("📊 Generating visualizations...")
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        analyzer.plot_all(save_to=str(output_path / "plots"), display=False)

        click.echo(click.style("   ├─ Biomarker distributions... ✓", fg="green"))
        click.echo(click.style("   ├─ ROC curves... ✓", fg="green"))
        click.echo(click.style("   └─ Enrichment impact chart... ✓", fg="green"))
        click.echo()
        click.echo("━" * 72)
        click.echo()

        # Step 6: Export results
        click.echo(f"💾 Exporting results to: {click.style(output_dir, fg='cyan', bold=True)}")
        click.echo()
        analyzer.export(output_dir=output_dir, format=output_format)

        click.echo("   Files created:")
        click.echo(f"   ├─ 📄 {Path(output_dir) / 'biomarker_rankings.csv'}")
        click.echo(f"   ├─ 📄 {Path(output_dir) / 'optimal_cutoffs.csv'}")
        click.echo(f"   ├─ 📄 {Path(output_dir) / 'enrichment_summary.json'}")
        click.echo(f"   ├─ 📄 {Path(output_dir) / 'recommended_criteria.txt'}")
        click.echo(f"   ├─ 📊 {Path(output_dir) / 'plots' / 'biomarker_distributions.png'}")
        click.echo(f"   ├─ 📊 {Path(output_dir) / 'plots' / 'roc_curves.png'}")
        click.echo(f"   └─ 📊 {Path(output_dir) / 'plots' / 'enrichment_impact.png'}")
        click.echo()
        click.echo("━" * 72)
        click.echo()

        # Success message
        click.echo(click.style("✅ Analysis complete!", fg="green", bold=True))
        click.echo()
        click.echo("   Next Steps:")
        click.echo(f"   1. Review biomarker rankings in {output_dir}/biomarker_rankings.csv")
        click.echo(f"   2. Examine plots in {output_dir}/plots/")
        click.echo(f"   3. Share {output_dir}/recommended_criteria.txt with clinical team")
        click.echo()
        click.echo("━" * 72)

    except Exception as e:
        click.echo(click.style(f"\n❌ Error: {str(e)}", fg="red", bold=True))
        import traceback

        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True),
    help="Path to CSV file to validate",
)
@click.option(
    "--outcome",
    "-o",
    required=True,
    help="Name of outcome column",
)
def validate(input_file, outcome):
    """
    Validate input data format and quality.

    Example:
        trialix validate --input trial.csv --outcome responder
    """
    try:
        click.echo(f"🔍 Validating data from: {click.style(input_file, fg='cyan', bold=True)}")
        click.echo()

        analyzer = TrialEnrichment(data=input_file, outcome=outcome)

        try:
            summary = analyzer.load_data()
            click.echo(click.style("✅ Data validation passed!", fg="green", bold=True))
            click.echo()
            click.echo("Data Summary:")
            click.echo(f"  ├─ Total patients: {summary.n_patients}")
            click.echo(f"  ├─ Responders: {summary.n_responders}")
            click.echo(f"  ├─ Non-responders: {summary.n_non_responders}")
            click.echo(f"  ├─ Response rate: {summary.response_rate * 100:.1f}%")
            click.echo(f"  ├─ Total biomarkers: {len(summary.biomarkers)}")
            click.echo(f"  ├─ Continuous biomarkers: {len(summary.continuous_biomarkers)}")
            click.echo(f"  └─ Categorical biomarkers: {len(summary.categorical_biomarkers)}")

        except ValueError as e:
            click.echo(click.style("❌ Data validation failed!", fg="red", bold=True))
            click.echo(f"\n{str(e)}")
            sys.exit(1)

    except Exception as e:
        click.echo(click.style(f"\n❌ Error: {str(e)}", fg="red", bold=True))
        sys.exit(1)


if __name__ == "__main__":
    cli()
