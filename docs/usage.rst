Usage Guide
===========

Command-Line Interface
----------------------

The CLI provides easy access to all monitoring features.

Getting Help
^^^^^^^^^^^^

.. code-block:: bash

    pixi run cli --help
    pixi run cli stats --help

Basic Statistics
^^^^^^^^^^^^^^^^

Get overall cluster statistics for the last 30 days:

.. code-block:: bash

    pixi run cli stats --days 30

Output formats:

.. code-block:: bash

    # Table format (default)
    pixi run cli stats --days 30

    # JSON format
    pixi run cli stats --days 30 --format json

    # CSV format with file export
    pixi run cli stats --days 30 --format csv --output stats.csv

    # JSON file export
    pixi run cli stats --days 30 --format json --output stats.json

User Breakdown
^^^^^^^^^^^^^^

Analyze resource usage by user:

.. code-block:: bash

    # Display in table format
    pixi run cli users --days 30

    # Export to CSV
    pixi run cli users --days 30 --output users.csv

Peak Usage Times
^^^^^^^^^^^^^^^^

Identify when the cluster is most busy:

.. code-block:: bash

    pixi run cli peak-times --days 30 --output peaks.json

Visualizations
^^^^^^^^^^^^^^

Generate interactive charts:

.. code-block:: bash

    # Core utilization over time
    pixi run cli visualize --metric core-utilization --days 30 --output util.html

    # User resource distribution
    pixi run cli visualize --metric user-distribution --days 30 --output users.html

    # Peak hours distribution
    pixi run cli visualize --metric peak-hours --days 30 --output peaks.html

    # Job duration statistics
    pixi run cli visualize --metric job-duration --days 30 --output duration.html

Interactive Dashboard
^^^^^^^^^^^^^^^^^^^^^

Create a comprehensive summary dashboard:

.. code-block:: bash

    pixi run cli dashboard --days 30 --output dashboard.html

Then open ``dashboard.html`` in your web browser.

REST API Server
---------------

Start the API server:

.. code-block:: bash

    pixi run api

The server runs at ``http://localhost:5000`` by default.

API Endpoints
^^^^^^^^^^^^^

**Health Check**

.. code-block:: bash

    curl http://localhost:5000/api/v1/health

**Overall Statistics**

.. code-block:: bash

    curl http://localhost:5000/api/v1/stats?days=30

**Per-User Statistics**

.. code-block:: bash

    curl http://localhost:5000/api/v1/users?days=30

**Core Utilization**

.. code-block:: bash

    curl http://localhost:5000/api/v1/utilization?days=30

**Peak Usage Times**

.. code-block:: bash

    curl http://localhost:5000/api/v1/peak-times?days=30

**Job Statistics**

.. code-block:: bash

    curl http://localhost:5000/api/v1/job-stats?days=30

**Cluster State**

.. code-block:: bash

    curl http://localhost:5000/api/v1/cluster-state

**Running Jobs**

.. code-block:: bash

    curl http://localhost:5000/api/v1/running-jobs

Python API
----------

Use SLURM Monitoring as a library in your Python code:

Basic Usage
^^^^^^^^^^^

.. code-block:: python

    from slurm_monitoring.collector import SlurmCollector
    from slurm_monitoring.analyzer import ClusterAnalyzer

    # Collect job history
    collector = SlurmCollector()
    jobs = collector.get_job_history(days=30)

    # Analyze data
    analyzer = ClusterAnalyzer(jobs)
    stats = analyzer.get_summary()

    # Print results
    print(f"Total core hours: {stats['utilization']['total_core_hours']}")
    print(f"Average cores per job: {stats['utilization']['average_cores_per_job']}")

Core Utilization
^^^^^^^^^^^^^^^^

.. code-block:: python

    from slurm_monitoring.analyzer import ClusterAnalyzer

    analyzer = ClusterAnalyzer(jobs)

    # Get overall utilization
    util = analyzer.compute_core_utilization()
    print(f"Total core hours: {util['total_core_hours']}")
    print(f"Max cores used: {util['max_cores_used']}")

    # Get hourly breakdown
    hourly = analyzer.utilization.get_hourly_stats()
    print(hourly)

    # Get daily breakdown
    daily = analyzer.utilization.get_daily_stats()
    print(daily)

User Analysis
^^^^^^^^^^^^^

.. code-block:: python

    # Per-user breakdown
    user_stats = analyzer.breakdown_by_user()
    for user, stats in user_stats.items():
        print(f"{user}: {stats['total_cores_allocated']} cores used")

    # Per-account breakdown
    account_stats = analyzer.breakdown_by_account()
    for account, stats in account_stats.items():
        print(f"{account}: {stats['job_count']} jobs")

Pattern Detection
^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Find peak usage times
    peaks = analyzer.identify_peak_times()
    print(f"Peak hour: {peaks['peak_hour']}")
    print(f"Jobs at peak: {peaks['jobs_at_peak']}")

    # Find idle periods
    idle = analyzer.identify_idle_periods()
    for period in idle[:5]:  # First 5 idle periods
        print(f"Idle from {period['start']} to {period['end']}")

Job Statistics
^^^^^^^^^^^^^^

.. code-block:: python

    # Job duration statistics
    duration_stats = analyzer.compute_job_duration_stats()
    print(f"Average duration: {duration_stats['average_duration_minutes']} minutes")
    print(f"Max duration: {duration_stats['max_duration_minutes']} minutes")

    # Job submission frequency
    frequency = analyzer.compute_job_frequency()
    print(f"Average jobs/day: {frequency['average_jobs_per_day']}")

Exporting Data
^^^^^^^^^^^^^^

.. code-block:: python

    from slurm_monitoring.exporters import JSONExporter, CSVExporter

    # Export to JSON
    json_exporter = JSONExporter()
    json_exporter.export(analyzer.get_summary(), "summary.json")

    # Export user stats to CSV
    csv_exporter = CSVExporter()
    csv_exporter.export_user_stats(user_stats, "users.csv")

Visualizations
^^^^^^^^^^^^^^

.. code-block:: python

    from slurm_monitoring.visualizers import PlotGenerator, Dashboard

    # Create plot generator
    plotter = PlotGenerator()

    # Plot core utilization over time
    hourly = analyzer.utilization.get_hourly_stats()
    plotter.plot_hourly_utilization(hourly, "utilization.html")

    # Plot user distribution
    user_stats = analyzer.breakdown_by_user()
    plotter.plot_user_distribution(user_stats, "users.html")

    # Create interactive dashboard
    dashboard = Dashboard()
    dashboard.create_summary_dashboard(analyzer.get_summary(), "dashboard.html")

Advanced Usage
--------------

Custom Data Filtering
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Get data for specific period
    collector = SlurmCollector()
    jobs = collector.get_job_history(days=7)

    # Get data for specific user
    user_jobs = jobs[jobs['User'] == 'username']

    # Filter by job state
    completed = jobs[jobs['State'] == 'COMPLETED']
    failed = jobs[jobs['State'] == 'FAILED']

Batch Processing
^^^^^^^^^^^^^^^^

.. code-block:: python

    from datetime import datetime, timedelta

    # Process data in chunks
    for days_back in range(0, 90, 30):
        start = days_back
        end = days_back + 30
        jobs = collector.get_job_history(days=start)
        analyzer = ClusterAnalyzer(jobs)
        print(f"Analysis for days {start}-{end}: {analyzer.get_summary()}")

Integration with Monitoring Systems
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    # Send to Prometheus
    from prometheus_client import start_http_server, Gauge

    core_hours = Gauge('slurm_core_hours_total', 'Total core hours')
    
    analyzer = ClusterAnalyzer(collector.get_job_history(days=1))
    stats = analyzer.compute_core_utilization()
    core_hours.set(stats['total_core_hours'])

Tips and Best Practices
-----------------------

#. **Lookback Period**: Use appropriate time windows (7 days for weekly trends, 30 days for monthly)
#. **Caching**: For repeated queries, save results to JSON/CSV to avoid repeated SLURM calls
#. **Error Handling**: Wrap collector calls in try-except for production code
#. **Performance**: For large datasets (>100k jobs), process in chunks or use daily aggregates
#. **Time Zones**: All timestamps are in cluster timezone; use pandas `tz_convert()` if needed

Example: Production Report Generator
-------------------------------------

.. code-block:: python

    from slurm_monitoring.collector import SlurmCollector
    from slurm_monitoring.analyzer import ClusterAnalyzer
    from slurm_monitoring.exporters import JSONExporter, CSVExporter
    from slurm_monitoring.visualizers import Dashboard
    from datetime import datetime

    def generate_weekly_report():
        collector = SlurmCollector()
        jobs = collector.get_job_history(days=7)
        analyzer = ClusterAnalyzer(jobs)

        # Generate summary
        summary = analyzer.get_summary()

        # Export
        timestamp = datetime.now().isoformat()
        json_exp = JSONExporter()
        json_exp.export(summary, f"reports/summary_{timestamp}.json")

        csv_exp = CSVExporter()
        csv_exp.export_user_stats(
            analyzer.breakdown_by_user(),
            f"reports/users_{timestamp}.csv"
        )

        # Dashboard
        dashboard = Dashboard()
        dashboard.create_summary_dashboard(
            summary,
            f"reports/dashboard_{timestamp}.html"
        )

        print(f"Report generated at {timestamp}")

    if __name__ == "__main__":
        generate_weekly_report()

Code Quality & Development
--------------------------

Type Hints & MyPy
^^^^^^^^^^^^^^^^^

The codebase uses type hints for better code quality and IDE support.

Static type checking with MyPy:

.. code-block:: bash

    # Run type checker
    pixi run type-check

    # Type check entire project
    mypy src/ --config-file=.mypy.ini

Configuration in `.mypy.ini`:

- Python version 3.9+
- Warning on untyped definitions
- Strict null checks
- Per-module library configurations

Example with type hints:

.. code-block:: python

    from typing import Optional, Dict, List
    import pandas as pd

    def breakdown_by_user(
        self, 
        jobs: Optional[pd.DataFrame] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Break down resource usage by user.
        
        Args:
            jobs: Job data (uses self.jobs_data if not provided)
            
        Returns:
            User statistics dictionary
        """
        pass

Pre-commit Hooks
^^^^^^^^^^^^^^^^

Automatically validate code quality before commits.

**Initial Setup**:

.. code-block:: bash

    # Install Git hooks
    pixi run pre-commit-install
    
    # Or using Make
    make pre-commit-install

**Running Checks**:

.. code-block:: bash

    # Run checks on changed files
    pre-commit run

    # Run checks on all files
    pixi run pre-commit-run
    # or
    make pre-commit

**What Gets Checked**:

- Code formatting (Black)
- Linting (Ruff with auto-fix)
- Type hints (MyPy)
- YAML/JSON syntax validation
- Large file detection
- Merge conflict markers
- Trailing whitespace
- Documentation coverage (>50%)

**Skip Hooks** (if needed):

.. code-block:: bash

    # Skip hooks for a commit
    git commit --no-verify

Full Workflow Example
^^^^^^^^^^^^^^^^^^^^^

Complete development workflow:

.. code-block:: bash

    # Install environment
    pixi install
    
    # Set up pre-commit hooks
    make pre-commit-install
    
    # Make code changes...
    
    # Test your changes
    pixi run test
    
    # Format and lint
    pixi run format
    pixi run lint
    
    # Type check
    pixi run type-check
    
    # Or run all quality checks
    pixi run quality
    
    # Commit (pre-commit hooks will run automatically)
    git add .
    git commit -m "Add new feature"
    
    # Build documentation
    pixi run docs-build

Development Tools Reference
^^^^^^^^^^^^^^^^^^^^^^^^^^^

+-----------+---------------------+-----------------+
| Tool      | Command             | Purpose         |
+===========+=====================+=================+
| Black     | pixi run format     | Code formatting |
+-----------+---------------------+-----------------+
| Ruff      | pixi run lint       | Linting         |
+-----------+---------------------+-----------------+
| MyPy      | pixi run type-check | Type checking   |
+-----------+---------------------+-----------------+
| Pytest    | pixi run test       | Unit testing    |
+-----------+---------------------+-----------------+
| Pre-commit| pixi run pre-commit-run | CI gates    |
+-----------+---------------------+-----------------+

See :doc:`deployment` for production deployment and :doc:`faq` for troubleshooting.
