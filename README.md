# SLURM Monitoring Tool

[![Tests](https://github.com/HealthyPear/slurm_monitor/actions/workflows/test.yml/badge.svg)](https://github.com/HealthyPear/slurm_monitor/actions/workflows/test.yml)
[![Documentation](https://github.com/HealthyPear/slurm_monitor/actions/workflows/docs.yml/badge.svg)](https://github.com/HealthyPear/slurm_monitor/actions/workflows/docs.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A comprehensive Python package for analyzing SLURM cluster statistics and core utilization patterns.

## Quick Links

* 📖 [Full Documentation](docs/) - Installation, usage, deployment, API reference
* 📊 [Architecture Guide](docs/architecture.rst) - System design and components
* 🚀 [Deployment Guide](docs/deployment.rst) - Production setup and operations
* ❓ [FAQ & Troubleshooting](docs/faq.rst) - Common questions and solutions
* 🤝 [Contributing Guide](CONTRIBUTING.md) - Development setup, code standards, contribution process

- **Core Utilization Analytics**: Track CPU core usage over time
- **Historical Analysis**: Analyze job duration and frequency from accounting data
- **User Attribution**: Breakdown statistics by user or account
- **Peak Pattern Detection**: Identify usage patterns and peak times
- **Multiple Data Sources**: Integrate sacct, sinfo, and squeue data
- **Multiple Output Formats**: CSV, JSON, CLI reports, Web API, and interactive visualizations
- **Web API**: REST API for querying cluster statistics
- **Interactive Dashboards**: Matplotlib and Plotly visualizations

## Installation

### Using Pixi (Recommended)

```bash
pixi install
pixi run cli --help
```

### Using pip

```bash
pip install -e .
slurm-stats --help
```

## Usage

### Command Line Interface

```bash
# Get overall statistics
slurm-stats stats --days 30

# User-specific breakdown
slurm-stats users --days 30

# Export to JSON
slurm-stats stats --days 30 --format json > report.json

# Generate visualization
slurm-stats visualize --metric core-utilization --days 30

# Get peak usage times
slurm-stats peak-times --days 30
```

### Web API

```bash
# Start the API server
pixi run api

# Query the API
curl http://localhost:5000/api/v1/stats
curl http://localhost:5000/api/v1/users
curl http://localhost:5000/api/v1/utilization?days=30
```

### Python API

```python
from slurm_monitoring.collector import SlurmCollector
from slurm_monitoring.analyzer import ClusterAnalyzer

# Collect data
collector = SlurmCollector()
jobs_data = collector.get_job_history(days=30)
cluster_state = collector.get_cluster_state()

# Analyze data
analyzer = ClusterAnalyzer(jobs_data)
stats = analyzer.compute_core_utilization()
user_breakdown = analyzer.breakdown_by_user()
peak_times = analyzer.identify_peak_times()

# Export results
analyzer.export_to_csv('stats.csv')
analyzer.export_to_json('stats.json')
```

## Project Structure

```
slurm_monitoring/
├── collector/          # SLURM data collection modules
│   ├── sacct.py       # Historical accounting data
│   ├── sinfo.py       # Cluster state information
│   └── squeue.py      # Running job information
├── analyzer/          # Data analysis modules
│   ├── utilization.py # Core utilization analysis
│   ├── patterns.py    # Pattern detection
│   └── aggregator.py  # Data aggregation
├── exporters/         # Output formatters
│   ├── csv_exporter.py
│   ├── json_exporter.py
│   └── report_generator.py
├── api/              # REST API server
│   ├── server.py     # Flask application
│   └── routes.py     # API endpoints
├── visualizers/      # Visualization modules
│   ├── plots.py      # Matplotlib/Plotly plots
│   └── dashboard.py  # Interactive dashboards
├── cli.py            # Command-line interface
└── config.py         # Configuration management
```

## Architecture

- **Collector**: Retrieves data from SLURM using `sacct`, `sinfo`, and `squeue` commands
- **Analyzer**: Processes and analyzes the collected data
- **Exporters**: Converts analyzed data to various output formats
- **API**: Provides REST endpoints for programmatic access
- **Visualizers**: Generates charts and interactive dashboards
- **CLI**: User-friendly command-line interface

## Building Documentation

Build comprehensive HTML documentation:

```bash
# Build with Pixi
pixi run docs-build

# Or with make
make docs

# View in browser
open docs/_build/html/index.html

# Serve locally
pixi run docs-serve
```

See [docs/README.md](docs/README.md) for detailed documentation instructions.

## Documentation Coverage

The documentation includes:

✅ **Installation Guide** - System requirements, installation methods, troubleshooting  
✅ **Usage Guide** - CLI commands, REST API, Python library with examples  
✅ **Deployment Guide** - Production deployment, process management, monitoring, security  
✅ **Architecture** - System design, component overview, data flow, extensibility  
✅ **API Reference** - Auto-generated documentation from code  
✅ **FAQ** - Common questions, troubleshooting, known limitations

## Development

### Setup

```bash
# Install development dependencies
pixi install

# Install pre-commit hooks (runs checks on each commit)
pixi run pre-commit-install
```

### Code Quality

The project uses modern development tools to maintain high code quality:

```bash
# Run all tests with coverage
pixi run test

# Format code with Black
pixi run format

# Lint with Ruff (auto-fixes issues)
pixi run lint

# Type checking with MyPy
pixi run type-check

# All quality checks
pixi run quality

# Run pre-commit hooks on all files
pixi run pre-commit-run
```

### Development Tools

- **Black** - Code formatting (100 char lines)
- **Ruff** - Fast Python linter 
- **MyPy** - Static type checking
- **Pytest** - Testing framework
- **Pre-commit** - Git hooks for automatic checks

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines, code standards, and workflow.

## Configuration

Create a `slurm_config.yaml` in your home directory or current directory:

```yaml
slurm:
  command_timeout: 30  # seconds
  host: localhost      # SLURM cluster head node (optional)
  port: 6817           # SLURM daemon port (optional)

collection:
  default_lookback_days: 30
  cache_dir: ~/.slurm-monitoring/cache

api:
  host: 0.0.0.0
  port: 5000
  debug: false

visualization:
  theme: "seaborn"
  output_format: "html"
```

## License

TBD
