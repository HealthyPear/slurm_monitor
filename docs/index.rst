SLURM Monitoring Documentation
==============================

A comprehensive Python package for analyzing SLURM cluster statistics and core utilization patterns.

.. image:: https://img.shields.io/badge/Python-3.9+-blue.svg
.. image:: https://img.shields.io/badge/License-MIT-green.svg

**SLURM Monitoring** provides tools for understanding how much compute resources are being used on your cluster, when they're used, and by whom. This information helps you make informed decisions about resource allocation and identify opportunities for optimization.

Quick Links
-----------

* :doc:`installation` - Get started with installation
* :doc:`usage` - Command-line and Python API usage
* :doc:`deployment` - Production deployment and operational guidelines
* :doc:`performance` - Performance tuning and optimization
* :doc:`contributing` - Development guide and contribution workflows
* :doc:`api` - Complete API reference

Features
--------

✨ **Comprehensive Analytics**
  - Core utilization tracking over time
  - Job duration and frequency analysis
  - Peak usage pattern detection
  - User and account-based breakdowns

📊 **Multiple Output Formats**
  - CSV and JSON export
  - Interactive Plotly dashboards
  - Matplotlib visualizations
  - CLI reports

🔌 **REST API**
  - Query statistics programmatically
  - Integrate with monitoring systems
  - Real-time cluster state information

📈 **Historical Analysis**
  - Analyze job accounting data
  - Identify trends over time
  - Compare usage patterns

Getting Started
---------------

Install and run in minutes:

.. code-block:: bash

    # Install Pixi (environment manager)
    brew install pixi

    # Setup project
    cd /path/to/slurm_monitoring
    pixi install

    # Run your first report
    pixi run cli stats --days 30

Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   installation
   usage
   deployment
   performance
   architecture
   api
   faq

Development & Contributing
---------------------------

.. toctree::
   :maxdepth: 2

   contributing
   code_quality
   quickref
   faq

Support
-------

For issues and questions:

- Check :doc:`faq` for common problems
- See :doc:`deployment` for operational guidance
- Review the `README.md <https://github.com/example/slurm-monitoring>`_ on GitHub

License
-------

MIT License - See LICENSE file for details
