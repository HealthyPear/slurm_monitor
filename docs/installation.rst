Installation
=============

System Requirements
-------------------

- **Python**: 3.9+
- **SLURM**: Client tools installed (sacct, sinfo, squeue)
- **OS**: Linux or macOS
- **Pixi**: For reproducible environment management (recommended)

Installing Pixi
---------------

**macOS**:

Provided you have Homebrew installed, you can install Pixi with the following command:

.. code-block:: bash

    brew install pixi

**Linux & macOS**:

This is the recommended installation method for Linux and macOS:

.. code-block:: bash

    curl -fsSL https://pixi.sh/install.sh | bash

**Other platforms**: See `pixi.sh <https://pixi.sh>`_ for installation instructions.

.. note::

    Pixi **0.84.1 or newer** is required (the manifest declares the glibc 2.17
    baseline on its ``platforms`` entries). With an older Pixi you will see
    ``expected a string, found table``. Upgrade with
    ``pixi self-update --version 0.84.1``.

Installing SLURM Monitoring
---------------------------

.. note::
    This project is not yet officially packaged, so you need first to clone the repository and install it manually.

Method 1: Using Pixi (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pixi ensures reproducible environments and handles all dependencies:

.. code-block:: bash

    # Clone or navigate to the project
    cd /path/to/slurm_monitoring

    # Install environment and dependencies
    pixi install

    # Verify installation
    pixi run cli --help

Method 2: Using pip
^^^^^^^^^^^^^^^^^^^

For manual installation without Pixi:

.. code-block:: bash

    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Install package
    pip install -e .

    # Verify installation
    slurm-stats --help

Development Installation
------------------------

For development and testing:

.. code-block:: bash

    # Install with Pixi (includes dev dependencies)
    pixi install

    # Run tests
    pixi run test

    # Format code
    pixi run format

    # Type checking
    pixi run type-check

Configuration
-------------

Create a configuration file at ``~/.slurm_config.yaml``:

.. code-block:: yaml

    slurm:
      command_timeout: 30
      # Optional: set if SLURM head node is remote
      # host: slurm-head.example.com

    collection:
      default_lookback_days: 30
      cache_dir: ~/.slurm-monitoring/cache

    api:
      host: 0.0.0.0
      port: 5000
      debug: false

    visualization:
      theme: seaborn
      output_format: html

See ``slurm_config.example.yaml`` in the project root for more options.

Troubleshooting Installation
----------------------------

**SLURM commands not found**

Ensure SLURM client tools are in your PATH:

.. code-block:: bash

    which sacct sinfo squeue

If not found, install SLURM client packages for your system.

**Pixi not working**

Try updating Pixi:

.. code-block:: bash

    pixi --version
    pixi self-update

**Connection issues to cluster**

Verify cluster connectivity:

.. code-block:: bash

    pixi run cli stats --days 1

Check your ``~/.slurm_config.yaml`` for correct host/port settings.

Next Steps
----------

After installation:

1. Check :doc:`usage` for CLI commands
2. See :doc:`deployment` for running in production
3. Review :doc:`api` for programmatic access
