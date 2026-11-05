"""Plot generation for SLURM statistics"""

import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class PlotGenerator:
    """Generates visualizations for cluster statistics"""

    def __init__(self, theme: str = "plotly_white"):
        """Initialize plot generator

        Args:
            theme: Plotly theme name (plotly, plotly_white, plotly_dark, ggplot2, seaborn, etc.)
        """
        self.theme = theme
        # Use plotly themes instead of matplotlib styles
        # Matplotlib seaborn style was deprecated in matplotlib 3.6+

    def plot_hourly_utilization(
        self, utilization_data: pd.Series, output_path: Optional[str] = None
    ):
        """
        Plot hourly core utilization

        Args:
            utilization_data: Series with hourly utilization counts
            output_path: Optional path to save as HTML
        """
        try:
            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=utilization_data.index,
                    y=utilization_data.values,
                    mode="lines+markers",
                    name="Core Hours",
                )
            )
            fig.update_layout(
                title="Hourly Core Utilization",
                xaxis_title="Time",
                yaxis_title="Core Hours",
                hovermode="x unified",
            )

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Saved hourly utilization plot to {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Failed to create hourly utilization plot: {e}")
            return None

    def plot_user_distribution(self, user_stats: Dict, output_path: Optional[str] = None):
        """
        Plot resource usage by user

        Args:
            user_stats: Dictionary with per-user statistics
            output_path: Optional path to save as HTML
        """
        try:
            users = list(user_stats.keys())
            cores = [user_stats[u].get("total_cores_allocated", 0) for u in users]

            fig = go.Figure()
            fig.add_trace(go.Bar(x=users, y=cores, name="Total Cores"))
            fig.update_layout(
                title="Core Allocation by User",
                xaxis_title="User",
                yaxis_title="Total Cores",
            )

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Saved user distribution plot to {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Failed to create user distribution plot: {e}")
            return None

    def plot_peak_hours(self, peak_data: Dict, output_path: Optional[str] = None):
        """
        Plot peak hours distribution

        Args:
            peak_data: Dictionary with peak hour information
            output_path: Optional path to save as HTML
        """
        try:
            top_hours = peak_data.get("top_hours", {})
            if not top_hours:
                logger.warning("No peak hours data available")
                return None

            hours = [int(h) for h in top_hours.keys()]
            counts = list(top_hours.values())

            fig = go.Figure()
            fig.add_trace(go.Bar(x=hours, y=counts, name="Job Count"))
            fig.update_layout(
                title="Top Job Submission Hours",
                xaxis_title="Hour of Day",
                yaxis_title="Number of Jobs",
                showlegend=False,
            )

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Saved peak hours plot to {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Failed to create peak hours plot: {e}")
            return None

    def plot_job_duration_distribution(
        self, duration_data: Dict, output_path: Optional[str] = None
    ):
        """Plot job duration distribution"""
        try:
            stats = [
                duration_data.get("min_duration_minutes", 0),
                duration_data.get("median_duration_minutes", 0),
                duration_data.get("average_duration_minutes", 0),
                duration_data.get("max_duration_minutes", 0),
            ]
            labels = ["Min", "Median", "Average", "Max"]

            fig = go.Figure()
            fig.add_trace(go.Bar(x=labels, y=stats, name="Duration (minutes)"))
            fig.update_layout(
                title="Job Duration Statistics",
                yaxis_title="Duration (minutes)",
                showlegend=False,
            )

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Saved duration distribution plot to {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Failed to create duration distribution plot: {e}")
            return None
