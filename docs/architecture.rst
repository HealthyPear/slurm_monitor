Architecture
============

System Overview
---------------

SLURM Monitoring follows a modular architecture with clear separation of concerns:

.. code-block:: text

    ┌─────────────────────────────────────────────────────┐
    │              User Interface Layer                   │
    ├─────────────────────────────────────────────────────┤
    │  CLI (click)  │  REST API (Flask)  │  Visualization │
    ├─────────────────────────────────────────────────────┤
    │          Analysis & Business Logic                  │
    ├─────────────────────────────────────────────────────┤
    │  Analyzer  │  Aggregator  │  Pattern Detection      │
    ├─────────────────────────────────────────────────────┤
    │              Data Collection Layer                  │
    ├─────────────────────────────────────────────────────┤
    │      sacct      │      sinfo      │     squeue      │
    ├─────────────────────────────────────────────────────┤
    │              SLURM Cluster                          │
    └─────────────────────────────────────────────────────┘

Core Components
---------------

Data Collection Layer
^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Gather raw data from SLURM cluster

**Modules**:

- **sacct** (``collector/sacct.py``): Historical job accounting
  - Queries job history using ``sacct`` command
  - Returns: job IDs, execution time, CPU allocation, user info
  - Lookback: Configurable (default 30 days)

- **sinfo** (``collector/sinfo.py``): Cluster state information
  - Queries node status using ``sinfo`` command
  - Returns: node count, CPUs, memory, states
  - Frequency: Real-time on-demand

- **squeue** (``collector/squeue.py``): Running job information
  - Queries job queue using ``squeue`` command
  - Returns: running/pending jobs, CPU usage, allocation
  - Frequency: Real-time on-demand

**Design Pattern**: Adapter pattern - wraps SLURM commands behind consistent Python interface

Analysis Layer
^^^^^^^^^^^^^^

**Purpose**: Process raw data into insights

**Modules**:

- **UtilizationAnalyzer** (``analyzer/utilization.py``)
  - Computes core-hour allocation
  - Generates time-series utilization
  - Outputs: hourly, daily, weekly buckets

- **PatternAnalyzer** (``analyzer/patterns.py``)
  - Identifies peak usage times
  - Finds idle periods
  - Analyzes job submission patterns
  - Computes day-of-week distribution

- **DataAggregator** (``analyzer/aggregator.py``)
  - Breaks down usage by user
  - Breaks down usage by account
  - Computes job duration statistics
  - Calculates submission frequency

**Design Pattern**: Strategy pattern - pluggable analysis strategies

Export & Visualization Layer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Purpose**: Present data to users

**Modules**:

- **Exporters**
  - JSONExporter: Structured data export for APIs/integration
  - CSVExporter: Tabular export for spreadsheet analysis

- **Visualizers**
  - PlotGenerator: Individual interactive plots using Plotly
  - Dashboard: Comprehensive dashboard with multiple charts

**Design Pattern**: Template method - consistent export/visualization interface

User Interface Layer
^^^^^^^^^^^^^^^^^^^^

**Purpose**: Provide access to functionality

**Interfaces**:

- **CLI (click)**
  - 6 main commands (stats, users, peak-times, visualize, dashboard, etc.)
  - Rich formatting and multiple output options
  - Local execution

- **REST API (Flask)**
  - 8 endpoints for programmatic access
  - JSON responses
  - Remote access via HTTP

- **Python Library**
  - Direct importable API for integration
  - Programmatic data access

Data Flow
---------

Typical Usage Flow
^^^^^^^^^^^^^^^^^^

.. code-block:: text

    User Request
         ↓
    [CLI/API/Library]
         ↓
    [Configuration]
         ↓
    [Collector] → SLURM Commands (sacct, sinfo, squeue)
         ↓
    [Raw Data] (DataFrame)
         ↓
    [Analyzer] (Utilization, Patterns, Aggregator)
         ↓
    [Processed Data] (Summary statistics)
         ↓
    [Exporters/Visualizers]
         ↓
    [Output] (JSON, CSV, HTML, tables)

Details by Command Type
^^^^^^^^^^^^^^^^^^^^^^^

**CLI Stats Command**:

.. code-block:: text

    $ pixi run cli stats --days 30
         ↓
    SlurmCollector.get_job_history(30)
         ↓
    SacctCollector.get_jobs(30)
         ↓
    subprocess.run(['sacct', ...])
         ↓
    Parse output → pandas.DataFrame
         ↓
    ClusterAnalyzer(jobs_df)
         ↓
    analyzer.get_summary()
         ↓
    Return formatted table

**API Users Endpoint**:

.. code-block:: text

    GET /api/v1/users?days=30
         ↓
    SlurmCollector.get_job_history(30)
         ↓
    ClusterAnalyzer.breakdown_by_user()
         ↓
    Dict with per-user stats
         ↓
    JSON serialization → HTTP response

**Python Direct Usage**:

.. code-block:: text

    from slurm_monitoring import SlurmCollector, ClusterAnalyzer
         ↓
    collector = SlurmCollector()
    jobs = collector.get_job_history(30)
         ↓
    analyzer = ClusterAnalyzer(jobs)
    user_stats = analyzer.breakdown_by_user()
         ↓
    Direct Python dict access

Key Design Decisions
--------------------

Subprocess-Based SLURM Integration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Why**: Uses ``sacct``, ``sinfo``, ``squeue`` commands directly

**Advantages**:
- No C library dependencies
- Automatic SLURM library compatibility
- Easy to debug (can test commands manually)
- Works with remote clusters via SSH

**Disadvantages**:
- Slight overhead from process spawning
- Requires SLURM client tools installed
- Timeout configuration needed

**Alternative Considered**: Direct SLURM library binding (PySlurm)
- Would require C compilation
- More complex deployment
- Tighter version coupling

Pandas for Data Analysis
^^^^^^^^^^^^^^^^^^^^^^^^

**Why**: Uses pandas DataFrames for data processing

**Advantages**:
- Powerful data manipulation
- Easy time-series operations
- Integration with numeric tools
- Familiar to data scientists

**Disadvantages**:
- Overhead for small datasets
- Memory usage for large datasets

**Alternative Considered**: Pure Python lists/dicts
- Simpler, but limited analytical capability

Flask for REST API
^^^^^^^^^^^^^^^^^^

**Why**: Lightweight Flask framework

**Advantages**:
- Minimal dependencies
- Easy to understand and extend
- Good for simple APIs
- Can be deployed anywhere

**Disadvantages**:
- Development-grade server (needs reverse proxy)
- Single-threaded by default

**Alternative Considered**: FastAPI
- Would require additional dependencies
- Overkill for current use case

Configuration Management
------------------------

Configuration Sources (in priority order):

1. **Default values** (conf.py)
2. **Config file** (``~/.slurm_config.yaml``) - optional
3. **Environment variables** (future extension)

This allows users to:
- Start with defaults
- Override with config file
- Override everything at runtime

Extensibility Points
--------------------

Adding New Data Sources
^^^^^^^^^^^^^^^^^^^^^^^

Create new collector in ``collector/`` directory:

.. code-block:: python

    class CustomCollector:
        def collect(self):
            # Gather and return data
            pass

Then integrate into ``SlurmCollector.__init__()``

Adding New Analysis
^^^^^^^^^^^^^^^^^^^

Create new analyzer class in ``analyzer/`` directory:

.. code-block:: python

    class NewAnalysis:
        def __init__(self, jobs_data):
            self.jobs_data = jobs_data

        def analyze(self):
            # Process and return results
            pass

Then add method to ``ClusterAnalyzer`` that delegates

Adding New Output Format
~~~~~~~~~~~~~~~~~~~~~~~~

Create new exporter in ``exporters/`` directory:

.. code-block:: python

    class NewExporter:
        def export(self, data, filepath):
            # Serialize data to format
            pass

Then integrate into CLI and API

Performance Characteristics
---------------------------

Data Collection
^^^^^^^^^^^^^^^

- **sacct**: O(n) where n = number of jobs (typically 100-1000ms for 30 days)
- **sinfo**: O(m) where m = number of nodes (typically <100ms)
- **squeue**: O(p) where p = running jobs (typically <100ms)

Analysis
^^^^^^^^

- Aggregation: O(n) - single pass through jobs
- Pattern detection: O(n log n) - sorting and grouping
- Time-series: O(n) - bucketing and aggregation

Memory Usage
^^^^^^^^^^^^

- 1000 jobs ≈ 100KB DataFrame
- 100,000 jobs ≈ 10MB DataFrame
- Most clusters: <50MB for 30-day window

Scalability Limits
^^^^^^^^^^^^^^^^^^

Practical limits with current implementation:

- **Jobs per query**: <1M (memory/time constraint)
- **Time window**: <1 year (SLURM usually caps at 90-365 days)
- **Concurrent API requests**: 10-20 (single Flask worker)

For larger scales, consider:
- Database caching (PostgreSQL + cache layer)
- Asynchronous processing (Celery + Kafka)
- Data warehouse (ClickHouse, Snowflake)

Testing Strategy
----------------

Unit Tests
^^^^^^^^^^

- Test individual components in isolation
- Use mock SLURM data
- Located in ``tests/``

Integration Tests
^^^^^^^^^^^^^^^^^

- Test component interactions
- Would require actual SLURM cluster
- Currently not included (future enhancement)

Manual Testing
^^^^^^^^^^^^^^

- Run on actual cluster
- Verify output formats
- Compare with expected results

See Testing section in :doc:`usage` for current test running.

Dependencies and Versions
--------------------------

Core Dependencies
^^^^^^^^^^^^^^^^^

- **Python**: 3.9+ (f-strings, type hints)
- **pandas**: 1.5+ (data manipulation)
- **click**: 8.1+ (CLI framework)
- **flask**: 2.3+ (REST API)
- **plotly**: 5.0+ (interactive visualization)
- **matplotlib**: 3.7+ (static plots)

Development Dependencies
^^^^^^^^^^^^^^^^^^^^^^^^

- **pytest**: 7.0+ (testing)
- **ruff**: 0.9+ (linting and formatting)
- **mypy**: 1.0+ (type checking)

See ``pyproject.toml`` and ``pixi.toml`` for complete version specifications.

Future Architecture Enhancements
--------------------------------

Potential improvements:

1. **Database Backend**: Store historical data in PostgreSQL
2. **Caching Layer**: Redis for API response caching
3. **Async Collectors**: Concurrent SLURM command execution
4. **Event System**: Real-time notifications for anomalies
5. **Plugin Architecture**: Allow user-defined collectors/analyzers
6. **GraphQL API**: Alternative to REST
7. **Web Dashboard**: React frontend for browser access
