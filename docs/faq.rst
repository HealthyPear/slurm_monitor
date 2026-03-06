FAQ & Troubleshooting
=====================

Frequently Asked Questions
--------------------------

Installation & Setup
^^^^^^^^^^^^^^^^^^^^

**Q: Do I need SLURM installed locally?**

A: You need SLURM client tools (``sacct``, ``sinfo``, ``squeue``). These are typically installed on login nodes. The SLURM server daemon is not required.

**Q: Can I run SLURM Monitoring on a machine without SLURM?**

A: Not with the current implementation. You need SLURM client tools. However, you could:

1. SSH to a login node and run it there
2. Install SLURM client tools on your monitoring server
3. Use a remote configuration that connects to a login node

**Q: How do I configure it for a remote SLURM cluster?**

A: Currently, commands are run locally. To monitor a remote cluster:

1. Run on the remote cluster's login node, or
2. Manually configure SSH tunneling, or
3. Set ``host`` in configuration (if remote SLURM daemon is available)

Future versions will have better remote support.

**Q: Is Pixi required?**

A: No, you can use pip: ``pip install -e .`` and run ``slurm-stats`` directly. Pixi is recommended for reproducible environments.

Data & Analysis
^^^^^^^^^^^^^^^

**Q: How far back can I analyze?**

A: Limited by SLURM's accounting database retention. Most clusters retain 30-365 days. Check with your SLURM administrator for your retention policy:

.. code-block:: bash

    sacct --help | grep starttime

**Q: Why is my data missing or incomplete?**

A: Common causes:

1. SLURM hasn't run any jobs in the lookback period
2. Accounting database is disabled
3. Job retention time is set short
4. Check: ``sacct -a --format=JobID | head``

**Q: Can I analyze just one user's jobs?**

A: Yes, modify the collector or filter results:

.. code-block:: python

    jobs = collector.get_job_history(days=30)
    user_jobs = jobs[jobs['User'] == 'username']
    analyzer = ClusterAnalyzer(user_jobs)

**Q: What's the maximum number of jobs I can analyze?**

A: Practically, 100,000-1,000,000 jobs depending on available memory. Typical clusters: <100,000 jobs/month.

**Q: Are my queries real-time?**

A: Almost. SLURM accounting data has slight delays (minutes). Running jobs (``squeue``) is real-time.

API & Server
^^^^^^^^^^^^

**Q: Can I use the API from a different machine?**

A: Yes, if you run the server with:

.. code-block:: yaml

    api:
      host: 0.0.0.0  # Listen on all interfaces
      port: 5000

Then access from: ``http://server-ip:5000/api/v1/stats``

For security in production, use a reverse proxy with authentication.

**Q: How do I secure the API?**

A: Use a reverse proxy:

- Nginx with HTTP authentication
- Apache with mod_auth
- Traefik with middleware
- Cloud provider API gateway (AWS API Gateway, etc.)

See :doc:`deployment` for details.

**Q: Can I run multiple API instances?**

A: Yes. Run on different ports or use a load balancer. Each instance can handle ~100-1000 requests/minute.

**Q: How do I integrate with my monitoring system?**

A: Use the REST API. See :doc:`deployment` for Prometheus/Grafana examples.

Performance & Troubleshooting
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Q: Why is data collection slow?**

A: ``sacct`` queries can be slow for large accounting databases (>1M entries). Solutions:

1. Reduce lookback period: ``--days 7`` instead of ``--days 30``
2. Increase timeout: Set ``command_timeout: 60`` in config
3. Increase SLURM accounting database performance (admin task)

**Q: No data available - what's wrong?**

A: Try these checks:

.. code-block:: bash

    # 1. Verify SLURM tools work
    which sacct sinfo squeue

    # 2. Check for any jobs
    sacct -a | head

    # 3. Try with shorter period
    pixi run cli stats --days 1

    # 3. Check SLURM is running
    sinfo

**Q: SLURM command not found**

A: SLURM client tools not installed. Install them:

.. code-block:: bash

    # Ubuntu/Debian
    apt-get install slurm-client

    # CentOS/RHEL
    yum install slurm

    # macOS (if SLURM is available)
    brew install slurm-llnl

**Q: Port 5000 already in use**

A: Either:

1. Stop other process: ``lsof -i :5000 | kill``
2. Use different port: Add to ``~/.slurm_config.yaml``:

   .. code-block:: yaml

       api:
         port: 5001

**Q: Memory getting too high**

A: For large queries, process in chunks:

.. code-block:: python

    # Instead of 90 days at once
    for days_offset in range(0, 90, 30):
        jobs = collector.get_job_history(days=days_offset)
        # Process...

Visualization
^^^^^^^^^^^^^

**Q: How do I embed visualizations in a website?**

A: Plotly HTML is standalone. Embed with an iframe:

.. code-block:: html

    <iframe src="path/to/dashboard.html" width="100%" height="600"></iframe>

**Q: Can I customize the dashboard colors?**

A: Currently limited options. You can:

1. Modify templates in ``visualizers/``
2. Generate custom plots in Jupyter notebooks
3. Integrate with BI tools (Tableau, Power BI)

**Q: How do I generate plots programmatically?**

A: Use the Python API:

.. code-block:: python

    from slurm_monitoring.visualizers import PlotGenerator

    plotter = PlotGenerator(theme='plotly_dark')
    plotter.plot_hourly_utilization(data, 'output.html')

Deployment
^^^^^^^^^^

**Q: Should I run on a login node?**

A: Yes! Login nodes are ideal. See :doc:`deployment` for details.

**Q: Can I run this in a container?**

A: Yes, but you need to mount SLURM configuration. Example Dockerfile:

.. code-block:: dockerfile

    FROM python:3.11
    RUN apt-get update && apt-get install -y slurm-client
    RUN pip install slurm-monitoring
    ENTRYPOINT ["slurm-stats"]

**Q: How do I set up automatic daily reports?**

A: Use cron (see :doc:`deployment`):

.. code-block:: bash

    0 0 * * * pixi run cli dashboard --days 30 --output /var/www/reports/daily.html

**Q: What are system requirements?**

A: Minimal:

- CPU: 1 core sufficient
- RAM: 512MB-2GB depending on cluster size
- Disk: 100MB for installation + space for reports/cache
- Network: Access to SLURM cluster head node

Customization
^^^^^^^^^^^^^

**Q: Can I add custom analysis?**

A: Yes! Create a new analyzer class in ``analyzer/`` and integrate it. See :doc:`architecture`.

**Q: Can I export to a database?**

A: Currently supports JSON/CSV. You can:

1. Extend CSVExporter for your database
2. Parse JSON output in ETL pipeline
3. Post to API metrics endpoint

**Q: Can I modify the CLI commands?**

A: Yes, edit ``cli.py`` to add new commands or change behavior.

**Q: How do I add new SLURM data sources?**

A: Create new collector in ``collector/`` directory and integrate. See :doc:`architecture`.

Common Issues & Solutions
--------------------------

Issue: "sacct: command not found"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Cause**: SLURM client tools not installed

**Solution**:

.. code-block:: bash

    # Find SLURM installation
    find /usr -name sacct 2>/dev/null

    # If not found, install
    apt-get install slurm-client  # Debian/Ubuntu
    yum install slurm              # CentOS/RHEL

    # Verify
    sacct --version

**Issue: "No data available"**

**Cause**: Empty accounting database or wrong period

**Solutions**:

.. code-block:: bash

    # Check if SLURM has data
    sacct -a --starttime=2024-01-01 | wc -l

    # Try shorter period
    pixi run cli stats --days 1

    # Check cluster has nodes
    sinfo

Issue: API "Address already in use"
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**:

.. code-block:: bash

    # Kill existing process
    lsof -i :5000 -t | xargs kill -9

    # Or use different port in ~/.slurm_config.yaml

Issue: Slow queries/Timeout
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solutions**:

1. Increase timeout:

   .. code-block:: bash

       cat >> ~/.slurm_config.yaml << EOF
       slurm:
         command_timeout: 60
       EOF

2. Reduce data range:

   .. code-block:: bash

       pixi run cli stats --days 7  # Instead of 30

3. Check SLURM database health (admin):

   .. code-block:: bash

       sacctmgr show stats

Issue: Visualizations won't open
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Ensure Plotly is installed:

.. code-block:: bash

    pixi list | grep plotly
    # If missing: pixi install

Issue: Configuration not being read
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Solution**: Check file location and format:

.. code-block:: bash

    # Expected location
    cat ~/.slurm_config.yaml

    # Validate YAML
    python -c "import yaml; yaml.safe_load(open('~/.slurm_config.yaml').read())"

Getting Help
------------

1. **Check this FAQ** - Most issues are documented here
2. **See :doc:`deployment`** - Operational guidelines and solutions
3. **Review code comments** - Helpful documentation in source
4. **Run with debug flag** (if available) for verbose output
5. **Check logs**:

   .. code-block:: bash

       journalctl -u slurm-api -f  # Systemd
       tail -f /var/log/slurm-api.log  # Syslog
       tail -f slurm-api.log  # Direct file

Reporting Bugs
--------------

If you find an issue:

1. Collect diagnostic info:

   .. code-block:: bash

       slurm-stats --version
       python --version
       sacct --version
       sinfo --version

2. Run in debug mode and note errors
3. Reproduce the issue consistently
4. Document steps to reproduce
5. Include configuration (sanitized)

Known Limitations
-----------------

- Remote clusters: Requires login node access or SSH tunneling
- Time zones: All timestamps in cluster timezone
- Job dependencies: Not analyzed
- Multi-cluster: Monitor one cluster at a time
- Real-time dashboards: Periodic polling only (no WebSocket)
- Large scales: >1M jobs may require optimization

Future Improvements
-------------------

- Database caching for historical analysis
- Remote cluster monitoring
- Multi-cluster dashboards
- Real-time WebSocket updates
- Machine learning for anomaly detection
- Web UI dashboard
- Prometheus metrics export
