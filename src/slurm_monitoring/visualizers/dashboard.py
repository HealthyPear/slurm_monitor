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
            fig = make_subplots(
                rows=2,
                cols=2,
                subplot_titles=(
                    "Core Utilization",
                    "User Breakdown",
                    "Peak Hours",
                    "Job Duration",
                ),
                specs=[[{}, {}], [{}, {}]],
            )

            # Utilization chart
            util = summary_data.get("utilization", {})
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=util.get("total_core_hours", 0),
                    title={"text": "Total Core Hours"},
                    domain={"x": [0, 0.5], "y": [0.5, 1]},
                ),
                row=1,
                col=1,
            )

            # User breakdown
            user_data = summary_data.get("user_breakdown", {})
            if user_data:
                users = list(user_data.keys())[:5]  # Top 5
                cores = [user_data[u].get("total_cores_allocated", 0) for u in users]
                fig.add_trace(go.Bar(x=users, y=cores, name="Cores"), row=1, col=2)

            # Peak times
            peak_data = summary_data.get("peak_times", {})
            if peak_data:
                top_hours = peak_data.get("top_hours", {})
                hours = list(top_hours.keys())
                counts = list(top_hours.values())
                fig.add_trace(go.Bar(x=hours, y=counts, name="Jobs"), row=2, col=1)

            # Job stats
            job_data = summary_data.get("job_stats", {})
            if job_data:
                stats = [
                    job_data.get("min_duration_minutes", 0),
                    job_data.get("average_duration_minutes", 0),
                    job_data.get("max_duration_minutes", 0),
                ]
                fig.add_trace(
                    go.Bar(x=["Min", "Avg", "Max"], y=stats, name="Job Duration"),
                    row=2,
                    col=2,
                )

            fig.update_layout(height=800, title_text="SLURM Cluster Statistics Dashboard")

            if output_path:
                fig.write_html(output_path)
                logger.info(f"Saved dashboard to {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")
            return None
