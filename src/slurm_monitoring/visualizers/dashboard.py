"""Interactive dashboards for SLURM statistics"""

import plotly.graph_objects as go
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class Dashboard:
    """Creates interactive dashboards for cluster statistics"""

    def create_summary_dashboard(
        self,
        summary_data: Dict,
        output_path: Optional[str] = None,
        figures: Optional[List[go.Figure]] = None,
    ):
        """
        Create a comprehensive summary dashboard

        Args:
            summary_data: Dictionary with summary statistics
            output_path: Optional path to save as HTML
            figures: Optional extra figures rendered below the summary on the same page
        """
        try:
            # Create a simple figure with no subplots first to avoid compatibility issues
            fig = go.Figure()

            # Get data safely
            util = summary_data.get("utilization", {})
            total_hours = float(util.get("total_core_hours", 0))
            avg_cores = float(util.get("average_cores_per_job", 0))
            max_cores = float(util.get("max_cores_used", 0))

            job_stats = summary_data.get("job_stats", {})
            avg_duration = float(job_stats.get("average_duration_minutes", 0))
            max_duration = float(job_stats.get("max_duration_minutes", 0))

            peak_times = summary_data.get("peak_times", {})
            peak_hour = int(peak_times.get("peak_hour", 0))

            # Create summary text
            summary_text = f"""
            <b>SLURM Cluster Statistics Summary</b><br><br>
            <b>Core Utilization:</b><br>
            • Total Core Hours: {total_hours:,.1f}<br>
            • Average Cores/Job: {avg_cores:.1f}<br>
            • Max Cores Used: {max_cores:.0f}<br><br>

            <b>Job Analysis:</b><br>
            • Average Job Duration: {avg_duration:.1f} minutes<br>
            • Max Job Duration: {max_duration:.1f} minutes<br><br>

            <b>Peak Usage:</b><br>
            • Peak Hour: Hour {peak_hour} (0-23)<br>
            """

            # Add summary as annotation
            fig.add_annotation(
                text=summary_text,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=14),
                xanchor="center",
                yanchor="middle",
                bordercolor="black",
                borderwidth=1,
                borderpad=20,
                bgcolor="rgba(240,240,240,0.8)",
            )

            fig.update_layout(
                height=450,
                title_text="SLURM Cluster Statistics Dashboard",
                showlegend=False,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                hovermode="closest",
            )

            if output_path:
                if figures:
                    self._write_combined_html([fig, *figures], output_path)
                else:
                    fig.write_html(output_path)
                logger.info(f"Saved dashboard to {output_path}")

            return fig

        except Exception as e:
            logger.error(f"Failed to create dashboard: {e}")

    @staticmethod
    def _write_combined_html(figures: List[go.Figure], output_path: str) -> None:
        """Write all figures into a single page, embedding plotly.js only once"""
        parts = [
            fig.to_html(full_html=False, include_plotlyjs=True if i == 0 else False)
            for i, fig in enumerate(figures)
        ]
        html = (
            "<html><head><meta charset='utf-8'>"
            "<title>SLURM Cluster Dashboard</title></head><body>"
            + "<hr>".join(parts)
            + "</body></html>"
        )
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
