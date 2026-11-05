API Reference
=============

This document provides comprehensive API documentation. For higher-level usage examples, see :doc:`usage`.

Collector Module
----------------

.. automodule:: slurm_monitoring.collector
   :members:
   :undoc-members:
   :show-inheritance:

Analyzer Module
---------------

.. automodule:: slurm_monitoring.analyzer
   :members:
   :undoc-members:
   :show-inheritance:

Exporters Module
----------------

.. automodule:: slurm_monitoring.exporters
   :members:
   :undoc-members:
   :show-inheritance:

Visualizers Module
------------------

.. automodule:: slurm_monitoring.visualizers
   :members:
   :undoc-members:
   :show-inheritance:

Config Module
-------------

.. automodule:: slurm_monitoring.config
   :members:
   :undoc-members:
   :show-inheritance:

Data Structures
---------------

Job History DataFrame
^^^^^^^^^^^^^^^^^^^^^

Structure returned by collectors (pandas DataFrame):

.. code-block:: python

    {
        'JobID': str,           # Job identifier
        'JobName': str,         # Job name
        'User': str,            # User who submitted job
        'Account': str,         # Account charged
        'State': str,           # Job state (COMPLETED, FAILED, etc.)
        'Start': datetime,      # Start time
        'End': datetime,        # End time
        'AllocCPUS': int,       # CPUs allocated
        'CPUTime': float,       # Total CPU time (minutes)
        'ExitCode': str,        # Exit code
    }

Statistics Dictionary
^^^^^^^^^^^^^^^^^^^^^

Structure returned by analysis methods:

.. code-block:: python

    {
        'utilization': {
            'total_core_hours': float,
            'average_cores_per_job': float,
            'max_cores_used': int,
            'min_cores_used': int,
        },
        'peak_times': {
            'peak_hour': int,
            'jobs_at_peak': int,
            'top_hours': {int: int},  # hour -> job_count
        },
        'user_breakdown': {
            'username': {
                'job_count': int,
                'total_cores_allocated': float,
                'average_cores_per_job': float,
                'total_cpu_hours': float,
            },
            ...
        },
        'job_stats': {
            'average_duration_minutes': float,
            'median_duration_minutes': float,
            'min_duration_minutes': float,
            'max_duration_minutes': float,
            'std_duration_minutes': float,
        },
    }

REST API Endpoints
------------------

All endpoints return JSON and support query parameters.

Base URL: ``http://localhost:5000/api/v1``

Health Check
^^^^^^^^^^^^

GET /health

**Response**:

.. code-block:: json

    {"status": "healthy"}

Overall Statistics
^^^^^^^^^^^^^^^^^^^

GET /stats?days=30

**Query Parameters**:

- ``days`` (int): Lookback period in days (default: 30)

**Response**: Summary statistics dictionary (see Data Structures)

**Example**:

.. code-block:: bash

    curl http://localhost:5000/api/v1/stats?days=30

Per-User Statistics
^^^^^^^^^^^^^^^^^^^^

GET /users?days=30

**Query Parameters**:

- ``days`` (int): Lookback period in days (default: 30)

**Response**: Dictionary with user breakdown

**Example**:

.. code-block:: bash

    curl http://localhost:5000/api/v1/users?days=30 | jq '.["user1"]'

Core Utilization
^^^^^^^^^^^^^^^^^

GET /utilization?days=30

**Query Parameters**:

- ``days`` (int): Lookback period in days (default: 30)

**Response**: Utilization statistics

**Example**:

.. code-block:: bash

    curl http://localhost:5000/api/v1/utilization?days=30

Peak Usage Times
^^^^^^^^^^^^^^^^

GET /peak-times?days=30

**Query Parameters**:

- ``days`` (int): Lookback period in days (default: 30)

**Response**: Peak hour information

**Example**:

.. code-block:: bash

    curl http://localhost:5000/api/v1/peak-times?days=30

Job Statistics
^^^^^^^^^^^^^^

GET /job-stats?days=30

**Query Parameters**:

- ``days`` (int): Lookback period in days (default: 30)

**Response**:

.. code-block:: json

    {
        "duration": {"average_minutes": 120},
        "frequency": {"total_jobs": 1500}
    }

Cluster State
^^^^^^^^^^^^^

GET /cluster-state

**Response**:

.. code-block:: json

    {
        "state": [],
        "summary": {
            "total_cpus": 1024,
            "total_memory_mb": 1048576,
            "node_states": {},
            "total_nodes": 16
        }
    }

Running Jobs
^^^^^^^^^^^^

GET /running-jobs

**Response**:

.. code-block:: json

    {
        "jobs": [],
        "summary": {
            "running": 25,
            "pending": 8,
            "total": 33,
            "total_cpus_in_use": 512
        }
    }

Error Responses
---------------

All endpoints return JSON error responses:

.. code-block:: json

    {
        "error": "Error description"
    }

Common HTTP Status Codes:

- ``200 OK``: Successful request
- ``400 Bad Request``: Invalid query parameters
- ``404 Not Found``: No data available for query
- ``500 Internal Server Error``: Server error (check logs)

Examples
--------

Typical API Usage
^^^^^^^^^^^^^^^^^

.. code-block:: python

    import requests

    # Get overall statistics
    response = requests.get(
        'http://localhost:5000/api/v1/stats',
        params={'days': 30}
    )
    stats = response.json()

    # Get user breakdown
    response = requests.get(
        'http://localhost:5000/api/v1/users',
        params={'days': 30}
    )
    users = response.json()

    # Find peak usage
    response = requests.get(
        'http://localhost:5000/api/v1/peak-times',
        params={'days': 7}
    )
    peaks = response.json()

Monitoring Integration
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    import requests
    import time

    def send_metrics(prom_gateway_url):
        """Send metrics to Prometheus pushgateway"""

        # Get stats
        response = requests.get(
            'http://localhost:5000/api/v1/stats',
            params={'days': 1}
        )
        stats = response.json()['utilization']

        # Format for Prometheus
        metrics = (
            "# HELP slurm_core_hours_total Total core hours used\\n"
            "# TYPE slurm_core_hours_total gauge\\n"
            f"slurm_core_hours_total {stats['total_core_hours']}\\n"
            "\\n"
            "# HELP slurm_avg_cores_per_job Average cores per job\\n"
            "# TYPE slurm_avg_cores_per_job gauge\\n"
            f"slurm_avg_cores_per_job {stats['average_cores_per_job']}\\n"
            "\\n"
            "# HELP slurm_max_cores_used Maximum cores used\\n"
            "# TYPE slurm_max_cores_used gauge\\n"
            f"slurm_max_cores_used {stats['max_cores_used']}\\n"
        )

        # Send to Prometheus
        response = requests.post(
            f'{prom_gateway_url}/metrics/job/slurm',
            data=metrics
        )
        return response.status_code == 200

    # Run periodically
    while True:
        send_metrics('http://prometheus:9091')
        time.sleep(300)  # Every 5 minutes

Library Usage
^^^^^^^^^^^^^

.. code-block:: python

    from slurm_monitoring import SlurmCollector, ClusterAnalyzer
    from slurm_monitoring.visualizers import Dashboard, PlotGenerator

    # Collect data
    collector = SlurmCollector()
    jobs = collector.get_job_history(days=30)

    # Analyze
    analyzer = ClusterAnalyzer(jobs)
    summary = analyzer.get_summary()

    # Generate visualizations
    plotter = PlotGenerator()
    dashboard = Dashboard()

    # Create plots
    dashboard.create_summary_dashboard(
        summary,
        'dashboard.html'
    )

    # Analyze specific user
    user_stats = analyzer.breakdown_by_user()
    for user, stats in user_stats.items():
        if stats['total_cores_allocated'] > 1000:
            print(f"Power user: {user}")
