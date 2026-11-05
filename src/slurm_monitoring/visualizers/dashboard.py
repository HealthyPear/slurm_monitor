"""Interactive dashboards for SLURM statistics"""

import html
import logging
from typing import Dict, List, Optional

import plotly.graph_objects as go

logger = logging.getLogger(__name__)

_PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>SLURM Cluster Dashboard</title>
<style>
body {{ font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
        margin: 0; background: #f5f6f8; color: #222; }}
main {{ max-width: 1100px; margin: 0 auto; padding: 24px; }}
h1 {{ font-size: 1.5rem; margin: 0 0 16px; }}
.card {{ background: #fff; border-radius: 8px; padding: 16px 20px;
         box-shadow: 0 1px 3px rgba(0,0,0,.12); margin-bottom: 20px; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; }}
th {{ background: #fafafa; width: 60%; font-weight: 600; }}
td {{ font-variant-numeric: tabular-nums; }}
.bar {{ display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #ddd;
        margin-bottom: 12px; flex-wrap: wrap; }}
.tab {{ border: 0; background: none; padding: 10px 16px; cursor: pointer;
        font-size: 0.95rem; border-bottom: 3px solid transparent; }}
.tab.active {{ border-bottom-color: #2a6fdb; color: #2a6fdb; font-weight: 600; }}
.spacer {{ flex: 1; }}
.panel {{ display: none; }}
.panel.active {{ display: block; }}
</style></head><body><main>
<h1>SLURM Cluster Statistics Dashboard</h1>
<div class="card">{summary}</div>
<div class="card">
<div class="bar">{buttons}<span class="spacer"></span>
<label><input type="checkbox" id="logy"> Log scale (y-axis)</label></div>
{panels}
</div>
</main>
<script>
const tabs = document.querySelectorAll('.tab');
const panels = document.querySelectorAll('.panel');
tabs.forEach(tab => tab.addEventListener('click', () => {{
  tabs.forEach(t => t.classList.toggle('active', t === tab));
  panels.forEach(p => p.classList.toggle('active', p.id === tab.dataset.target));
  const plot = document.querySelector('#' + tab.dataset.target + ' .plotly-graph-div');
  if (plot) Plotly.Plots.resize(plot);
}}));
document.getElementById('logy').addEventListener('change', e => {{
  document.querySelectorAll('.plotly-graph-div').forEach(plot =>
    Plotly.relayout(plot, {{'yaxis.type': e.target.checked ? 'log' : 'linear'}}));
}});
</script></body></html>
"""


class Dashboard:
    """Creates interactive dashboards for cluster statistics"""

    @staticmethod
    def _summary_table(summary_data: Dict) -> str:
        util = summary_data.get("utilization", {})
        job_stats = summary_data.get("job_stats", {})
        peak = summary_data.get("peak_times", {})
        rows = [
            ("Total core hours", f"{float(util.get('total_core_hours', 0)):,.1f}"),
            ("Average cores per job", f"{float(util.get('average_cores_per_job', 0)):.1f}"),
            ("Max cores used", f"{float(util.get('max_cores_used', 0)):.0f}"),
            (
                "Average job duration",
                f"{float(job_stats.get('average_duration_minutes', 0)):.1f} min",
            ),
            (
                "Median job duration",
                f"{float(job_stats.get('median_duration_minutes', 0)):.1f} min",
            ),
            ("Max job duration", f"{float(job_stats.get('max_duration_minutes', 0)):.1f} min"),
            ("Peak hour", f"{int(peak.get('peak_hour', 0)):02d}:00"),
        ]
        body = "".join(
            f"<tr><th>{html.escape(k)}</th><td>{html.escape(v)}</td></tr>" for k, v in rows
        )
        return f"<table>{body}</table>"

    def create_summary_dashboard(
        self,
        summary_data: Dict,
        output_path: Optional[str] = None,
        figures: Optional[List[go.Figure]] = None,
    ) -> str:
        """
        Create a dashboard page: a summary table plus one tab per figure

        Args:
            summary_data: Dictionary with summary statistics
            output_path: Optional path to save as HTML
            figures: Figures shown in tabs, titled after their plot title

        Returns:
            The dashboard HTML
        """
        figures = figures or []
        buttons, panels = [], []
        for i, fig in enumerate(figures):
            title = html.escape(fig.layout.title.text or f"Plot {i + 1}")
            active = " active" if i == 0 else ""
            buttons.append(f'<button class="tab{active}" data-target="panel{i}">{title}</button>')
            plot_html = fig.to_html(
                full_html=False,
                include_plotlyjs=True if i == 0 else False,
                default_width="100%",
            )
            panels.append(f'<div class="panel{active}" id="panel{i}">{plot_html}</div>')

        page = _PAGE.format(
            summary=self._summary_table(summary_data),
            buttons="".join(buttons),
            panels="".join(panels),
        )
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(page)
            logger.info(f"Saved dashboard to {output_path}")
        return page
