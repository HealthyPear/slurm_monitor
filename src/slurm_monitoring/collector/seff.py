"""Collector for SLURM seff command output for job efficiency metrics"""

import subprocess
import logging
import re
from typing import Dict, List, Optional, Any
import pandas as pd

from slurm_monitoring.config import Config

logger = logging.getLogger(__name__)


class SeffCollector:
    """Collects job efficiency metrics using seff command"""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize seff collector

        Args:
            config_file: Path to SLURM configuration file
        """
        self.config = Config(config_file or "slurm_config.yaml")
        self.seff_config = self.config.config.get("seff", {})
        self.timeout = self.seff_config.get("timeout", 30)

    def get_job_efficiency(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get efficiency metrics for a single job

        Args:
            job_id: SLURM job ID

        Returns:
            Dict with efficiency metrics (CPU, memory, GPU utilization, etc.)
        """
        return self._run_seff_command(job_id)

    def get_job_efficiency_batch(self, job_ids: List[str]) -> pd.DataFrame:
        """Get efficiency metrics for multiple jobs

        Args:
            job_ids: List of SLURM job IDs

        Returns:
            DataFrame with efficiency data for all jobs
        """
        results = []

        for job_id in job_ids:
            try:
                metrics = self.get_job_efficiency(job_id)
                if metrics:
                    results.append(metrics)
            except Exception as e:
                logger.warning(f"Failed to get efficiency for job {job_id}: {e}")

        if not results:
            return pd.DataFrame()

        return pd.DataFrame(results)

    def identify_inefficient_jobs(
        self, job_ids: List[str], cpu_threshold: float = 50.0, memory_threshold: float = 50.0
    ) -> pd.DataFrame:
        """Identify inefficient jobs based on utilization thresholds

        Args:
            job_ids: List of SLURM job IDs
            cpu_threshold: CPU efficiency threshold (%) below which job is inefficient
            memory_threshold: Memory efficiency threshold (%) below which job is inefficient

        Returns:
            DataFrame with inefficient jobs
        """
        df = self.get_job_efficiency_batch(job_ids)

        if df.empty:
            return df

        # Find jobs below both thresholds
        inefficient = df[
            (df["cpu_efficiency"] < cpu_threshold) & (df["memory_efficiency"] < memory_threshold)
        ]

        return inefficient.sort_values("cpu_efficiency")

    def _run_seff_command(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Run seff command and parse output

        Args:
            job_id: SLURM job ID

        Returns:
            Dict with parsed efficiency metrics, or None on error
        """
        try:
            result = subprocess.run(
                ["seff", job_id], capture_output=True, text=True, timeout=self.timeout, check=False
            )

            if result.returncode != 0:
                logger.warning(f"seff command failed for job {job_id}: {result.stderr}")
                return None

            return self._parse_seff_output(result.stdout, job_id)

        except subprocess.TimeoutExpired:
            logger.error(f"seff command timed out after {self.timeout}s for job {job_id}")
            return None
        except Exception as e:
            logger.error(f"Error running seff for job {job_id}: {e}")
            return None

    def _parse_seff_output(self, output: str, job_id: str) -> Dict[str, Any]:
        """Parse seff command output

        Args:
            output: Raw seff output
            job_id: The job ID

        Returns:
            Dict with parsed metrics
        """
        metrics: Dict[str, Any] = {
            "job_id": job_id,
            "state": None,
            "nodes": None,
            "cpus": None,
            "cpu_efficiency": None,
            "memory_allocated": None,
            "memory_used": None,
            "memory_efficiency": None,
            "wall_time_allocated": None,
            "wall_time_used": None,
            "wall_time_efficiency": None,
        }

        lines = output.strip().split("\n")

        for line in lines:
            line = line.strip()

            # Extract Job ID
            if "Job ID:" in line:
                metrics["job_id"] = line.split("Job ID:")[1].strip().split()[0]

            # Extract State
            if "State:" in line:
                metrics["state"] = line.split("State:")[1].strip().split()[0]

            # Extract Nodes
            if "Nodes:" in line:
                match = re.search(r"Nodes:\s+(\d+)", line)
                if match:
                    metrics["nodes"] = int(match.group(1))

            # Extract CPU Count
            if "Cores per node:" in line:
                match = re.search(r"Cores per node:\s+(\d+)", line)
                if match:
                    metrics["cpus"] = int(match.group(1))

            # Extract CPU Efficiency
            if "CPU Efficiency:" in line:
                match = re.search(r"CPU Efficiency:\s+([\d.]+)%", line)
                if match:
                    metrics["cpu_efficiency"] = float(match.group(1))

            # Extract Memory Allocated
            if "Memory Allocated:" in line:
                match = re.search(r"Memory Allocated:\s+([\d.]+)\s*([KMGT])?B?", line)
                if match:
                    value = float(match.group(1))
                    unit = match.group(2) or ""
                    metrics["memory_allocated"] = self._convert_memory(value, unit)

            # Extract Memory Used
            if "Memory Used:" in line:
                match = re.search(r"Memory Used:\s+([\d.]+)\s*([KMGT])?B?", line)
                if match:
                    value = float(match.group(1))
                    unit = match.group(2) or ""
                    metrics["memory_used"] = self._convert_memory(value, unit)

            # Extract Memory Efficiency
            if "Memory Efficiency:" in line:
                match = re.search(r"Memory Efficiency:\s+([\d.]+)%", line)
                if match:
                    metrics["memory_efficiency"] = float(match.group(1))

            # Extract Walltime
            if "Elapsed (wall clock) time:" in line:
                match = re.search(r"Elapsed \(wall clock\) time:\s+(.+)", line)
                if match:
                    time_str = match.group(1).strip()
                    metrics["wall_time_used"] = self._parse_time_string(time_str)

        # Calculate memory efficiency if not already set
        if (
            metrics["memory_allocated"]
            and metrics["memory_used"]
            and not metrics["memory_efficiency"]
        ):
            if metrics["memory_allocated"] > 0:
                metrics["memory_efficiency"] = (
                    metrics["memory_used"] / metrics["memory_allocated"] * 100
                )

        return metrics

    @staticmethod
    def _convert_memory(value: float, unit: str) -> float:
        """Convert memory to GB

        Args:
            value: Memory value
            unit: Unit (K, M, G, T)

        Returns:
            Memory in GB
        """
        multipliers = {
            "K": 1e-6,
            "M": 1e-3,
            "G": 1.0,
            "T": 1e3,
        }
        return value * multipliers.get(unit, 1.0)

    @staticmethod
    def _parse_time_string(time_str: str) -> float:
        """Parse time string to seconds

        Args:
            time_str: Time string (e.g., "01:23:45" or "1 day 2:34:56")

        Returns:
            Time in seconds
        """
        total_seconds = 0

        # Handle "X days Y:Z:W" format
        if "day" in time_str:
            parts = time_str.split()
            days = int(parts[0])
            time_part = parts[2]
            total_seconds += days * 86400
        else:
            time_part = time_str

        # Parse H:M:S
        time_components = time_part.split(":")
        if len(time_components) == 3:
            hours, minutes, seconds = map(int, time_components)
            total_seconds += hours * 3600 + minutes * 60 + seconds

        return total_seconds
