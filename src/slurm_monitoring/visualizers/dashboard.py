"""Interactive dashboards for SLURM statistics"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Dashboard:
    """Creates interactive dashboards for cluster statistics"""

    def create_summary_dashboard(self, summary_data: Dict, output_path: Optional[str] = None):
        """
        Create a comprehensive summary dashboard

        Args:
            summary_data: Dictionary with summary statistics
            output_path: Optional path to save as HTML
        """
        try:
            # Create subplots for bar/line charts (not indicators)
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "Core Utilization (Total Hours)",
                    "Top Users by Cores",
                    "Peak Usage Hours",
                    "Job Duration Analysis",
                ),
                specs=[[{"type": "bar"}, {"type": "bar"}], [{"type": "bar"}, {"type": "bar"}]],
            )

            # Core utilization as bar chart (instead of gauge indicator)
            util = summary_data.get("utilization", {})
            total_hours = util.get("total_core_hours", 0)
            avg_cores = util.get("average_cores_per_job", 0)
            fig.add_trace(
                go.Bar(
                    x=["Total Core Hours", "Avg Cores/Job"],
                    y=[total_hours, avg_cores],
                    marker_color=["#1f77b4", "#ff7f0e"],
                    showlegend=False,
                ),
                row=1,
                col=1,
            )

            # User breakdown
            user_data = summary_data.get("user_breakdown", {})
            if user_data:
                # Get top 5 users by core allocation
                sorted_users = sorted(
                    user_data.items(),
                    key=lambda x: x[1].get("total_cores_allocated", 0),
                    reverse=True,
                )[:5]
                users = [u[0] for u in sorted_users]
                cores = [u[1].get("total_cores_allocated", 0) for u in sorted_users]
                fig.add_trace(go.Bar(x=users, y=cores, name="Cores", showlegend=False), row=1, col=2)

            # Peak times
            peak_data = summary_data.get("peak_times", {})
            if peak_data:
                top_hours = peak_data.get("top_hours", {})
                if top_hours:
                    hours = [f"Hour {h}" for h in sorted(top_hours.keys())]
                    counts = [top_hours[int(h.split()[-1])] for h in hours]
                    fig.add_trace(go.Bar(x=hours, y=counts, name="Jobs", showlegend=False), row=2, col=1)

            # Job duration stats
            job_data = summary_data.get("job_stats", {})
            if job_data:
                stats = [
                    job_data.get("min_duration_minutes", 0),
                    job_data.get("average_duration_minutes", 0),
                    job_data.get("median_duration_minutes", 0),
                    job_data.get("max_duration_minutes", 0),
                ]
                fig.add_trace(
                    go.Bar(
                        x=["Min", "Avg", "Median", "Max"],
                        y=stats,
                        marker_color=["#2ca02c", "#d62728", "#9467bd", "#8c564b"],
                        showlegend=False,
                    ),
                    row=2,
                    col=2,
                )

            # Update axes labels
            fig.update_xaxes(title_text="Metric", row=1, col=1)
            fig.update_xaxes(title_text="User", row=1, col=2)
            fig.update_xaxes(title_text="Hour", row=2, col=1)
            fig.update_xaxes(title_text="Duration Type", row=2, col=2)

            fig.update_yaxes(title_text="Value", row=1, col=1)
            fig.update_yaxes(title_text="Cores", row=1, col=2)
            fig.update_yaxes(title_text="Job Count", row=2, col=1)
            fig.update_yaxes(title_text="Minutes", row=2, col=2)

            fig.update_layout(
                height=800, 
                title_text="SLURM Cluster Statistics Dashboard",
                showlegend=False,
                hovermode="x unified",
            )

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Saved dashboard to {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
