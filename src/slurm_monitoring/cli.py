"""Command-line interface for SLURM monitoring"""

import click
from pathlib import Path
from typing import Optional
import logging
from datetime import datetime

from .collector import SlurmCollector
from .collector.sreport import SreportCollector
from .collector.seff import SeffCollector
from .analyzer import ClusterAnalyzer
from .analyzer.efficiency import EfficiencyAnalyzer
from .exporters import CSVExporter, JSONExporter
from .visualizers import PlotGenerator, Dashboard

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Context settings to enable -h as help alias
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def cli():
    """SLURM cluster statistics and monitoring tool"""
    pass


@cli.command(context_settings=CONTEXT_SETTINGS)
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
            output_file = output or "stats.json"
            exporter = JSONExporter()
            exporter.export(stats, output_file)
            click.echo(f"Exported to {output_file}")
        elif format == "csv":
            output_file = output or "stats.csv"
            exporter = CSVExporter()
            exporter.export(stats, output_file)
            click.echo(f"Exported to {output_file}")
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


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--days", default=30, help="Number of days to analyze")
@click.option("--output", type=click.Path(), default="users.csv", help="Output file path")
def users(days: int, output: str):
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

        exporter = CSVExporter()
        exporter.export_user_stats(user_stats, output)
        click.echo(f"Exported to {output}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command(context_settings=CONTEXT_SETTINGS)
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


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--days", default=30, help="Number of days to analyze")
@click.option(
    "--metric",
    type=click.Choice(["core-utilization", "user-distribution", "peak-hours", "job-duration"]),
    default="core-utilization",
    help="Metric to visualize",
)
@click.option(
    "--output", type=click.Path(), default=None, help="Output HTML file (defaults to <metric>.html)"
)
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

        # Use default filename based on metric if output not specified
        output_file = output or f"{metric.replace('-', '_')}.html"

        if metric == "core-utilization":
            data = analyzer.utilization.get_daily_stats()
            plot_gen.plot_hourly_utilization(data, output_file)
        elif metric == "user-distribution":
            data = analyzer.breakdown_by_user()
            plot_gen.plot_user_distribution(data, output_file)
        elif metric == "peak-hours":
            data = analyzer.identify_peak_times()
            plot_gen.plot_peak_hours(data, output_file)
        elif metric == "job-duration":
            data = analyzer.compute_job_duration_stats()
            plot_gen.plot_job_duration_distribution(data, output_file)

        click.echo(f"Visualization saved to {output_file}")

    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command(context_settings=CONTEXT_SETTINGS)
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


@cli.command(context_settings=CONTEXT_SETTINGS)
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


@cli.command(context_settings=CONTEXT_SETTINGS)
def collect_snapshot():
    """Record current queue state for historical tracking"""
    try:
        from .collector.history import HistoryCollector
        
        click.echo("Recording queue snapshot...")
        collector = SlurmCollector()
        queue_summary = collector.squeue.get_summary()
        
        history = HistoryCollector()
        history.record_snapshot(queue_summary)
        
        click.echo(f"Snapshot recorded: {queue_summary['total']} jobs ({queue_summary['running']} running, {queue_summary['pending']} pending)")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option("--hours", default=24, help="Hours of history to analyze")
def trends(hours: int):
    """Show queue trends from historical snapshots"""
    try:
        from .collector.history import HistoryCollector
        
        history = HistoryCollector()
        trends_data = history.get_trends(hours=hours)
        
        if not trends_data:
            click.echo("No historical data available")
            return
        
        click.echo(f"\n=== QUEUE TRENDS (Last {hours} hours) ===\n")
        click.echo(f"Snapshots collected: {trends_data['snapshots_collected']}")
        click.echo(f"\nRunning Jobs:")
        click.echo(f"  Average: {trends_data['avg_running']:.0f}")
        click.echo(f"  Min: {trends_data['min_running']}")
        click.echo(f"  Max: {trends_data['max_running']}")
        
        click.echo(f"\nPending Jobs:")
        click.echo(f"  Average: {trends_data['avg_pending']:.0f}")
        click.echo(f"  Min: {trends_data['min_pending']}")
        click.echo(f"  Max: {trends_data['max_pending']}")
        
        click.echo(f"\nTotal Jobs in Queue:")
        click.echo(f"  Average: {trends_data['avg_total']:.0f}")
        click.echo(f"  Min: {trends_data['min_total']}")
        click.echo(f"  Max: {trends_data['max_total']}")
        
        latest = trends_data['latest_snapshot']
        click.echo(f"\nLatest Snapshot ({latest['timestamp']}):")
        click.echo(f"  Running: {latest['running']}")
        click.echo(f"  Pending: {latest['pending']}")
        click.echo(f"  Total: {latest['total']}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--metric",
    type=click.Choice(["user", "account", "cluster"]),
    default="user",
    help="Report metric to retrieve",
)
@click.option(
    "--start",
    type=str,
    default=None,
    help="Start date (YYYY-MM-DD)",
)
@click.option(
    "--end",
    type=str,
    default=None,
    help="End date (YYYY-MM-DD)",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path",
)
def sreport(metric: str, start: Optional[str], end: Optional[str], output: Optional[str]):
    """Get cluster accounting reports from sreport"""
    try:
        click.echo("Collecting sreport data...")
        collector = SreportCollector()
        
        if metric == "user":
            df = collector.get_account_utilization_by_user(start, end)
            output_file = output or "sreport_users.csv"
            click.echo(f"\nTop Users by Resource Usage:")
            click.echo(df.to_string())
        elif metric == "account":
            df = collector.get_account_utilization_by_account(start, end)
            output_file = output or "sreport_accounts.csv"
            click.echo(f"\nAccount Utilization:")
            click.echo(df.to_string())
        else:  # cluster
            metrics = collector.get_cluster_utilization(start, end)
            output_file = output or "sreport_cluster.json"
            click.echo(f"\nCluster Utilization:")
            for key, value in metrics.items():
                click.echo(f"  {key}: {value}")
        
        if output and df is not None:
            df.to_csv(output_file, index=False)
            click.echo(f"\nExported to {output_file}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--job-id",
    type=str,
    default=None,
    help="Single job ID to analyze",
)
@click.option(
    "--batch-file",
    type=click.Path(exists=True),
    default=None,
    help="File with job IDs (one per line)",
)
@click.option(
    "--show-waste",
    is_flag=True,
    help="Show only inefficient jobs",
)
@click.option(
    "--cpu-threshold",
    type=float,
    default=50,
    help="CPU efficiency threshold (%) for waste detection",
)
@click.option(
    "--memory-threshold",
    type=float,
    default=50,
    help="Memory efficiency threshold (%) for waste detection",
)
@click.option(
    "--output",
    type=click.Path(),
    default=None,
    help="Output file path (CSV)",
)
def efficiency(job_id: Optional[str], batch_file: Optional[str], show_waste: bool,
               cpu_threshold: float, memory_threshold: float, output: Optional[str]):
    """Analyze job efficiency metrics"""
    try:
        collector = SeffCollector()
        job_ids = []
        
        if job_id:
            job_ids = [job_id]
        elif batch_file:
            with open(batch_file) as f:
                job_ids = [line.strip() for line in f if line.strip()]
        else:
            click.echo("Please provide --job-id or --batch-file", err=True)
            return
        
        click.echo(f"Analyzing efficiency for {len(job_ids)} job(s)...")
        df = collector.get_job_efficiency_batch(job_ids)
        
        if df.empty:
            click.echo("No efficiency data found")
            return
        
        # Analyze
        analyzer = EfficiencyAnalyzer(df)
        
        if show_waste:
            click.echo(f"\nJobs with efficiency below thresholds:")
            waste = analyzer.identify_waste_opportunities(cpu_threshold, memory_threshold)
            if waste.empty:
                click.echo("No wasteful jobs found!")
            else:
                for _, job in waste.iterrows():
                    click.echo(
                        f"  Job {job['job_id']}: "
                        f"CPU={job.get('cpu_efficiency', 0):.1f}%, "
                        f"Mem={job.get('memory_efficiency', 0):.1f}%"
                    )
        else:
            # Show summary
            stats = analyzer.get_summary_statistics()
            click.echo(f"\n=== EFFICIENCY SUMMARY ===")
            click.echo(f"Total Jobs: {stats.get('total_jobs', 0)}")
            
            cpu = stats.get("cpu_efficiency", {})
            click.echo(f"\nCPU Efficiency:")
            click.echo(f"  Average: {cpu.get('average', 0):.1f}%")
            click.echo(f"  Min: {cpu.get('min', 0):.1f}%")
            click.echo(f"  Max: {cpu.get('max', 0):.1f}%")
            
            mem = stats.get("memory_efficiency", {})
            click.echo(f"\nMemory Efficiency:")
            click.echo(f"  Average: {mem.get('average', 0):.1f}%")
            click.echo(f"  Min: {mem.get('min', 0):.1f}%")
            click.echo(f"  Max: {mem.get('max', 0):.1f}%")
            
            # Recommendations
            click.echo(f"\nRecommendations:")
            for rec in analyzer.get_recommendations(cpu_threshold, memory_threshold):
                click.echo(f"  {rec}")
        
        # Export if requested
        if output:
            df.to_csv(output, index=False)
            click.echo(f"\nExported to {output}")
            
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        logger.exception(e)


def main():
    """Entry point for CLI"""
    cli()


if __name__ == "__main__":
    main()
