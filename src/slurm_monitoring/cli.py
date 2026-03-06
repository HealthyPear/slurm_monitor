"""Command-line interface for SLURM monitoring"""

import click
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime

from .collector import SlurmCollector
from .analyzer import ClusterAnalyzer
from .exporters import CSVExporter, JSONExporter
from .visualizers import PlotGenerator, Dashboard

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
@click.version_option()
def cli():
    """SLURM cluster statistics and monitoring tool"""
    pass


@cli.command()
@click.option(
    "--days",
    default=30,
    help="Number of days to analyze",
)
@click.option(
    "--format",
    type=click.Choice(["table", "json", "csv"]),
    default="table",
    help="Output format",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path",
)
def stats(days: int, format: str, output: Optional[str]):
    """Get overall cluster statistics"""
    try:
        click.echo(f"Collecting data for the last {days} days...")
        collector = SlurmCollector()
        jobs = collector.get_job_history(days=days)

        if jobs.empty:
            click.echo("No job data found for the specified period")
            return

        click.echo(f"Found {len(jobs)} jobs")

        analyzer = ClusterAnalyzer(jobs)
        stats = analyzer.get_summary()

        if format == "json":
            if output:
                exporter = JSONExporter()
                exporter.export(stats, output)
                click.echo(f"Exported to {output}")
            else:
                import json

                click.echo(json.dumps(stats, indent=2, default=str))
        elif format == "csv":
            if output:
                exporter = CSVExporter()
                exporter.export(stats, output)
                click.echo(f"Exported to {output}")
            else:
                click.echo("CSV output requires --output flag")
        else:

            click.echo("\n=== CLUSTER STATISTICS ===\n")
            util = stats.get("utilization", {})
            click.echo("Core Utilization:")
            click.echo(f"  Total Core Hours: {util.get('total_core_hours', 0):.1f}")
            click.echo(f"  Avg Cores/Job: {util.get('average_cores_per_job', 0):.1f}")
            click.echo(f"  Max Cores: {util.get('max_cores_used', 0):.0f}")

            job_stats = stats.get("job_stats", {})
            click.echo("\nJob Duration:")
            click.echo(
                f"  Average: {job_stats.get('average_duration_minutes', 0):.1f} minutes"
            )
            click.echo(f"  Median: {job_stats.get('median_duration_minutes', 0):.1f} minutes")

            peak_times = stats.get("peak_times", {})
            click.echo(f"\nPeak Usage: Hour {peak_times.get('peak_hour', 0)}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command()
@click.option("--days", default=30, help="Number of days to analyze")
@click.option("--output", type=click.Path(), default=None, help="Output file path")
def users(days: int, output: Optional[str]):
    """Get per-user resource breakdown"""
    try:
        click.echo(f"Collecting user data for the last {days} days...")
        collector = SlurmCollector()
        jobs = collector.get_job_history(days=days)

        if jobs.empty:
            click.echo("No job data found")
            return

        analyzer = ClusterAnalyzer(jobs)
        user_stats = analyzer.breakdown_by_user()

        if output:
            exporter = CSVExporter()
            exporter.export_user_stats(user_stats, output)
            click.echo(f"Exported to {output}")
        else:
            click.echo("\n=== USER RESOURCE USAGE ===\n")
            for user, stats in sorted(user_stats.items(), key=lambda x: x[1]["total_cores_allocated"], reverse=True):
                click.echo(f"{user}:")
                click.echo(f"  Jobs: {stats['job_count']}")
                click.echo(f"  Total Cores: {stats['total_cores_allocated']:.0f}")
                click.echo(f"  Avg Cores/Job: {stats['average_cores_per_job']:.1f}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command()
@click.option("--days", default=30, help="Number of days to analyze")
@click.option("--output", type=click.Path(), default="peak_times.json", help="Output file")
def peak_times(days: int, output: str):
    """Identify peak usage times"""
    try:
        click.echo(f"Analyzing peak times for the last {days} days...")
        collector = SlurmCollector()
        jobs = collector.get_job_history(days=days)

        if jobs.empty:
            click.echo("No job data found")
            return

        analyzer = ClusterAnalyzer(jobs)
        peak_data = analyzer.identify_peak_times()

        exporter = JSONExporter()
        exporter.export(peak_data, output)

        click.echo(f"\nPeak hour: {peak_data.get('peak_hour', 0)}")
        click.echo(f"Jobs at peak: {peak_data.get('jobs_at_peak', 0)}")
        click.echo(f"Exported to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command()
@click.option("--days", default=30, help="Number of days to analyze")
@click.option(
    "--metric",
    type=click.Choice(["core-utilization", "user-distribution", "peak-hours", "job-duration"]),
    default="core-utilization",
    help="Metric to visualize",
)
@click.option("--output", type=click.Path(), default=None, help="Output HTML file")
def visualize(days: int, metric: str, output: Optional[str]):
    """Generate visualizations"""
    try:
        click.echo(f"Generating {metric} visualization...")
        collector = SlurmCollector()
        jobs = collector.get_job_history(days=days)

        if jobs.empty:
            click.echo("No job data found")
            return

        analyzer = ClusterAnalyzer(jobs)
        plot_gen = PlotGenerator()

        if metric == "core-utilization":
            data = analyzer.utilization.get_daily_stats()
            plot_gen.plot_hourly_utilization(data, output)
        elif metric == "user-distribution":
            data = analyzer.breakdown_by_user()
            plot_gen.plot_user_distribution(data, output)
        elif metric == "peak-hours":
            data = analyzer.identify_peak_times()
            plot_gen.plot_peak_hours(data, output)
        elif metric == "job-duration":
            data = analyzer.compute_job_duration_stats()
            plot_gen.plot_job_duration_distribution(data, output)

        if output:
            click.echo(f"Visualization saved to {output}")
        else:
            click.echo("Use --output to save visualization")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command()
@click.option("--format", type=click.Choice(["table", "json"]), default="table", help="Output format")
def queue(format: str):
    """Show current job queue status (pending and running jobs)"""
    try:
        click.echo("Checking current job queue...")
        collector = SlurmCollector()
        queue_summary = collector.squeue.get_summary()

        if format == "json":
            import json
            click.echo(json.dumps(queue_summary, indent=2))
        else:
            click.echo("\n=== CURRENT JOB QUEUE ===\n")
            click.echo(f"Running Jobs:  {queue_summary.get('running', 0)}")
            click.echo(f"Pending Jobs:  {queue_summary.get('pending', 0)}")
            click.echo(f"Total Jobs:    {queue_summary.get('total', 0)}")
            
            total_cpus = queue_summary.get('total_cpus_in_use', 0)
            if total_cpus > 0:
                click.echo(f"CPUs In Use:   {total_cpus:.0f}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command()
@click.option("--days", default=30, help="Number of days to analyze")
@click.option("--output", type=click.Path(), default="dashboard.html", help="Output HTML file")
def dashboard(days: int, output: str):
    """Generate interactive dashboard"""
    try:
        click.echo(f"Generating dashboard for the last {days} days...")
        collector = SlurmCollector()
        jobs = collector.get_job_history(days=days)

        if jobs.empty:
            click.echo("No job data found")
            return

        analyzer = ClusterAnalyzer(jobs)
        summary = analyzer.get_summary()

        dash = Dashboard()
        dash.create_summary_dashboard(summary, output)

        click.echo(f"Dashboard saved to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


def main():
    """Entry point for CLI"""
    cli()


if __name__ == "__main__":
    main()
