Performance Tuning
==================

This guide explains how to optimize the SLURM monitoring tool for your environment, particularly when dealing with large clusters or slow SLURM command responses.

Common Performance Issues
-------------------------

**sacct command is slow or timing out**:

The `sacct` command can be slow when:
- Querying all users across the cluster (use `include_all_users: false`)
- Requesting many data fields (simplify the `format_fields` list)
- Looking back many days (reduce `default_lookback_days`)
- The cluster has a large job history

**Solution**: Use the configuration file to tune these settings for your cluster.

Configuration File Location
----------------------------

Create a configuration file in one of these locations (the first one found is
used, in this order):

1. ``./slurm_config.yaml`` (current directory)
2. ``~/.slurm_config.yaml`` (home directory) - recommended
3. ``~/slurm_config.yaml`` (home directory, without the leading dot)
4. ``~/.config/slurm_monitoring/config.yaml``
5. ``/etc/slurm_monitoring/config.yaml``

Performance Tuning Guide
------------------------

Fast Configuration
~~~~~~~~~~~~~~~~~~~

Use this for quick queries with minimal data:

.. code-block:: yaml

    sacct:
      timeout: 60                    # Shorter timeout
      include_all_users: false       # Only your user's jobs
      format_fields:                 # Minimal fields
        - JobID
        - User
        - AllocCPUS
        - State

    collection:
      default_lookback_days: 7       # Shorter lookback

**Performance**: ~5-10 seconds for typical queries

Balanced Configuration
~~~~~~~~~~~~~~~~~~~~~~

Good default for most clusters:

.. code-block:: yaml

    sacct:
      timeout: 120
      include_all_users: false
      format_fields:
        - JobID
        - JobName
        - User
        - Account
        - Start
        - End
        - AllocCPUS
        - State

    collection:
      default_lookback_days: 30

**Performance**: ~15-30 seconds for typical queries

Comprehensive Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For detailed analysis (slower but more data):

.. code-block:: yaml

    sacct:
      timeout: 300                   # Longer timeout
      include_all_users: true        # All users
      format_fields:                 # All fields
        - JobID
        - JobName
        - User
        - Account
        - Start
        - End
        - CPUTime
        - AllocCPUS
        - State
        - ExitCode

    collection:
      default_lookback_days: 90      # Longer lookback

**Performance**: ~30-120 seconds depending on cluster size

Tuning Parameters
-----------------

``sacct.timeout`` (seconds)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

How long to wait for `sacct` to complete. Increase if:
- Your cluster is large
- sacct command is slow
- Jobs history is extensive

**Recommended values**:
- Small clusters: 60-90 seconds
- Medium clusters: 120-180 seconds
- Large clusters: 180-300 seconds

``sacct.include_all_users``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Whether to query all users or just current user.

**false** (default, faster):
- Queries only your jobs: ``sacct -u $USER``
- Best for: Individual users, regular reporting
- Speed: Fast

**true** (slower):
- Queries all cluster jobs: ``sacct -a``
- Best for: System administrators, cluster-wide analysis
- Speed: Much slower (2-10x slower than per-user)

``sacct.include_steps``
~~~~~~~~~~~~~~~~~~~~~~~~

Whether to also return job steps (``.batch``, ``.extern``, ...).

**false** (default):
- Job-level records only: ``sacct --allocations``
- Job counts, durations and core-hours are not inflated by steps

**true**:
- Includes every step row; overrides per run with ``stats --include-steps``

``sacct.format_fields``
~~~~~~~~~~~~~~~~~~~~~~~~

List of fields to retrieve from `sacct`. Fewer fields = faster queries.

**Minimal fields** (fastest):
.. code-block:: yaml

    format_fields:
      - JobID
      - User
      - AllocCPUS
      - State

**Standard fields** (balanced):
.. code-block:: yaml

    format_fields:
      - JobID
      - JobName
      - User
      - Account
      - Start
      - End
      - AllocCPUS
      - State

**All fields** (slowest but most complete):
.. code-block:: yaml

    format_fields:
      - JobID
      - JobName
      - User
      - Account
      - Start
      - End
      - CPUTime
      - AllocCPUS
      - State
      - ExitCode

Common field choices:
- ``JobID`` - Job identifier (always include)
- ``User`` - Job owner
- ``Start``, ``End`` - Job times
- ``AllocCPUS`` - Cores allocated
- ``CPUTime`` - Total CPU time (slower to compute)
- ``State`` - Job status
- ``Account`` - Billing account

``collection.default_lookback_days``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Number of days to analyze by default. Shorter periods are faster.

**Recommended values**:
- Daily monitoring: 1-7 days (very fast)
- Weekly reports: 7-14 days (fast)
- Monthly reports: 30 days (normal)
- Trend analysis: 90-365 days (slow)

Optimization Tips
-----------------

**For CLI Commands**:

If `pixi run cli users` is slow, create ~/.slurm_config.yaml:

.. code-block:: yaml

    sacct:
      timeout: 120
      include_all_users: false
      format_fields:
        - JobID
        - User
        - AllocCPUS
        - State

**For REST API**:

If API endpoints timeout, adjust the config and restart the API server:

.. code-block:: bash

    # Create config with faster settings
    cat > ~/.slurm_config.yaml << 'EOF'
    sacct:
      timeout: 240
      include_all_users: false
    EOF

    # Restart API server
    pixi run api

**For Scheduled Monitoring**:

For cron jobs or monitors, use separate configs:

.. code-block:: bash

    # Fast daily collection for current user
    cat > ~/.slurm_config.daily.yaml << 'EOF'
    sacct:
      include_all_users: false
      format_fields:
        - JobID
        - User
        - AllocCPUS
    collection:
      default_lookback_days: 1
    EOF

    # Full weekly analysis for all users
    cat > ~/.slurm_config.weekly.yaml << 'EOF'
    sacct:
      timeout: 300
      include_all_users: true
      format_fields:
        - JobID
        - User
        - AllocCPUS
        - State
    collection:
      default_lookback_days: 7
    EOF

Testing Configuration Changes
------------------------------

Test your configuration quickly:

.. code-block:: bash

    # Run a single command with verbose output
    pixi run cli stats --days 7

    # Time the command
    time pixi run cli users

    # Try with minimal fields
    cat > ~/.slurm_config.yaml << 'EOF'
    sacct:
      include_all_users: false
      format_fields:
        - JobID
        - User
        - AllocCPUS
    EOF

    time pixi run cli users

Troubleshooting
---------------

**sacct still timing out**

If sacct times out even with optimal config:

1. Check SLURM database status:

   .. code-block:: bash

       # Manually run sacct
       time sacct -u $USER --starttime=2024-01-01 | head -20

2. If sacct itself is slow, contact your cluster administrator:

   .. code-block:: bash

       # Ask your cluster admin to check SLURM database
       slurm-nodelist

3. As a workaround, use shorter time periods:

   .. code-block:: yaml

       collection:
         default_lookback_days: 1  # Query only today

**High memory usage**

If the tool uses too much memory:

1. Reduce lookback days:

   .. code-block:: yaml

       collection:
         default_lookback_days: 7

2. Reduce fields in sacct:

   .. code-block:: yaml

       sacct:
         format_fields:
           - JobID
           - User
           - AllocCPUS

3. Run separate queries instead of all-at-once:

   .. code-block:: bash

       # Query one week at a time rather than 90 days
       pixi run cli stats --days 7

Benchmarking Your Configuration
--------------------------------

Use this script to benchmark different configurations:

.. code-block:: bash

    #!/bin/bash

    echo "Testing sacct performance..."

    # Test 1: Minimal fields
    echo "1. Minimal fields (JobID, User, AllocCPUS):"
    time sacct -u $USER --starttime=2026-03-01 \
      --format=JobID,User,AllocCPUS --parsable2 > /dev/null

    # Test 2: Standard fields
    echo "2. Standard fields (add State, Start, End):"
    time sacct -u $USER --starttime=2026-03-01 \
      --format=JobID,User,State,Start,End,AllocCPUS --parsable2 > /dev/null

    # Test 3: With all users (-a flag)
    echo "3. All users + all fields:"
    time sacct -a --starttime=2026-03-01 \
      --format=JobID,User,State,Start,End,CPUTime,AllocCPUS,ExitCode --parsable2 > /dev/null

Next Steps
----------

1. Create a configuration file: ``cp slurm_config.example.yaml ~/.slurm_config.yaml``
2. Adjust settings based on your needs
3. Test with: ``pixi run cli stats --days 7``
4. Monitor performance and iterate
5. See :doc:`deployment` for production setup

For more information, see:
- :doc:`faq` - Common questions
- :doc:`deployment` - Production deployment
- :doc:`usage` - Usage examples
