Deployment and Operations
==========================

Overview
--------

SLURM Monitoring is designed to run on SLURM login nodes and can be deployed for continuous monitoring, periodic reporting, or integration with existing monitoring systems.

Deployment Models
-----------------

Login Node Deployment (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Ideal for**: Single cluster, minimal operational overhead

**Advantages**:

- SLURM client tools and accounting database always available
- No network configuration needed
- Easy to troubleshoot and maintain
- Lightweight resource usage

**Setup**:

1. Install on login node:

   .. code-block:: bash

       ssh login.host
       cd /opt/slurm_monitoring  # or your preferred location
       pixi install

2. Configure (optional):

   .. code-block:: bash

       cat > ~/.slurm_config.yaml << EOF
       slurm:
         command_timeout: 30
       collection:
         default_lookback_days: 30
       api:
         host: 0.0.0.0
         port: 5000
       EOF

3. Test:

   .. code-block:: bash

       pixi run cli stats --days 7

Monitoring Server Deployment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Ideal for**: Multiple clusters, high availability, external monitoring

**Advantages**:

- Centralized monitoring for multiple clusters
- Dedicated resources for API server
- Better for large-scale deployments
- Easier to integrate with monitoring infrastructure

**Setup**:

1. Install on monitoring server with network access to cluster:

   .. code-block:: bash

       cd /opt/slurm_monitoring
       pixi install

2. Configure for remote cluster:

   .. code-block:: bash

       cat > ~/.slurm_config.yaml << EOF
       slurm:
         command_timeout: 30
         host: slurm-head.example.com
       EOF

3. Start API server (see Process Management section)

Periodic Data Collection
------------------------

Using Cron
^^^^^^^^^^

Schedule regular statistics collection:

.. code-block:: bash

    # Edit crontab
    crontab -e

    # Add entries:
    # Hourly statistics
    0 * * * * cd /opt/slurm_monitoring && pixi run cli stats --days 7 --format json --output /var/log/slurm-stats/hourly.json

    # Daily reports
    0 0 * * * cd /opt/slurm_monitoring && pixi run cli dashboard --days 30 --output /var/www/reports/daily.html

    # Weekly user breakdown
    0 1 * * 0 cd /opt/slurm_monitoring && pixi run cli users --days 7 --output /var/log/slurm-stats/weekly_users.csv

Using Systemd Timer
^^^^^^^^^^^^^^^^^^^^

For more control, create systemd timer units:

**File**: ``/etc/systemd/system/slurm-monitoring.service``

.. code-block:: ini

    [Unit]
    Description=SLURM Monitoring Data Collection
    After=network.target

    [Service]
    Type=oneshot
    User=slurm
    ExecStart=/home/slurm/.pixi/bin/pixi run -C /opt/slurm_monitoring cli stats --days 30 --format json --output /var/log/slurm-stats/data.json
    StandardOutput=journal
    StandardError=journal

**File**: ``/etc/systemd/system/slurm-monitoring.timer``

.. code-block:: ini

    [Unit]
    Description=Run SLURM Monitoring hourly
    Requires=slurm-monitoring.service

    [Timer]
    OnBootSec=5min
    OnUnitActiveSec=1h
    Persistent=true

    [Install]
    WantedBy=timers.target

Enable and start:

.. code-block:: bash

    sudo systemctl daemon-reload
    sudo systemctl enable slurm-monitoring.timer
    sudo systemctl start slurm-monitoring.timer
    sudo systemctl status slurm-monitoring.timer

API Server Process Management
-----------------------------

Using tmux (Simple)
^^^^^^^^^^^^^^^^^^^^

For development or temporary deployments:

.. code-block:: bash

    # Create persistent session
    tmux new-session -d -s slurm-api -c /opt/slurm_monitoring

    # Start server in session
    tmux send-keys -t slurm-api "pixi run api" Enter

    # Monitor
    tmux attach -t slurm-api

    # Stop
    tmux kill-session -t slurm-api

Using Systemd Service
^^^^^^^^^^^^^^^^^^^^^

For production deployments:

**File**: ``/etc/systemd/system/slurm-api.service``

.. code-block:: ini

    [Unit]
    Description=SLURM Monitoring API Server
    After=network.target

    [Service]
    Type=simple
    User=slurm
    WorkingDirectory=/opt/slurm_monitoring
    ExecStart=/home/slurm/.pixi/bin/pixi run api
    Restart=always
    RestartSec=10
    StandardOutput=journal
    StandardError=journal
    Environment="PATH=/home/slurm/.pixi/bin:/usr/local/bin:/usr/bin:/bin"

    [Install]
    WantedBy=multi-user.target

Enable and manage:

.. code-block:: bash

    sudo systemctl daemon-reload
    sudo systemctl enable slurm-api
    sudo systemctl start slurm-api
    sudo systemctl status slurm-api
    sudo systemctl restart slurm-api

    # View logs
    sudo journalctl -u slurm-api -f

Using Supervisord
^^^^^^^^^^^^^^^^^

For systems without systemd:

**File**: ``/etc/supervisor/conf.d/slurm-api.conf``

.. code-block:: ini

    [program:slurm-api]
    command=/home/slurm/.pixi/bin/pixi run -C /opt/slurm_monitoring api
    directory=/opt/slurm_monitoring
    autostart=true
    autorestart=true
    redirect_stderr=true
    stdout_logfile=/var/log/slurm-api.log
    user=slurm

Enable and start:

.. code-block:: bash

    sudo supervisorctl reread
    sudo supervisorctl update
    sudo supervisorctl start slurm-api

Reverse Proxy Setup
-------------------

Running Behind Nginx
^^^^^^^^^^^^^^^^^^^^

For production, run the API behind a reverse proxy:

**File**: ``/etc/nginx/sites-available/slurm-monitoring``

.. code-block:: nginx

    server {
        listen 80;
        server_name monitoring.cluster.local;

        # Optional: redirect to HTTPS
        # return 301 https://$server_name$request_uri;

        location /api/ {
            proxy_pass http://localhost:5000/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_buffering off;
        }

        # Serve reports/dashboards
        location /reports/ {
            alias /var/www/reports/;
            autoindex on;
        }
    }

Enable:

.. code-block:: bash

    sudo ln -s /etc/nginx/sites-available/slurm-monitoring /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx

Data Storage and Archival
--------------------------

Setting Up Data Directories
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Create data directories
    mkdir -p /var/log/slurm-stats
    mkdir -p /var/www/reports
    mkdir -p /opt/slurm_monitoring/.cache

    # Set permissions
    chmod 755 /var/log/slurm-stats
    chmod 755 /var/www/reports
    chown slurm:slurm /opt/slurm_monitoring/.cache

Automated Archival
^^^^^^^^^^^^^^^^^^^

Keep historical reports:

.. code-block:: bash

    # Archive old reports (keep 90 days)
    find /var/www/reports -name "*.html" -mtime +90 -exec gzip {} \;
    find /var/www/reports -name "*.gz" -mtime +365 -delete

    # Add to cron (weekly)
    0 0 * * 0 find /var/www/reports -name "*.html" -mtime +90 -exec gzip {} \;

Sharing Reports and Dashboards
-------------------------------

Overview
^^^^^^^^

Generated HTML reports and dashboards can be shared with team members through several methods depending on your infrastructure and access requirements.

Option 1: Shared Network Folder (Simplest)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Best for**: Small teams, existing shared storage

**Setup**:

.. code-block:: bash

    # Generate reports to shared location
    mkdir -p /mnt/shared/cluster_reports
    pixi run cli dashboard --output /mnt/shared/cluster_reports/dashboard_$(date +%Y%m%d).html --days 30
    pixi run cli visualize --metric core-utilization --output /mnt/shared/cluster_reports/core_util.html --days 30

**User Access**:

- Windows: ``\\server\shared\cluster_reports\dashboard_20260306.html``
- Linux/Mac: ``file:///mnt/shared/cluster_reports/dashboard_20260306.html``

**Automation**:

.. code-block:: bash

    # Daily report generation (add to crontab)
    0 9 * * * cd /opt/slurm_monitoring && pixi run cli dashboard --output /mnt/shared/cluster_reports/dashboard_$(date +\%Y\%m\%d).html --days 30

Option 2: Web Server with HTTP Access (Recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Best for**: Team access, professional appearance, centralized management

**Setup with Nginx**:

.. code-block:: bash

    # 1. Create web directory
    sudo mkdir -p /var/www/html/slurm-reports
    sudo chown www-data:www-data /var/www/html/slurm-reports
    sudo chmod 755 /var/www/html/slurm-reports

    # 2. Generate initial reports
    pixi run cli dashboard --output /var/www/html/slurm-reports/dashboard.html --days 30
    pixi run cli visualize --metric core-utilization --output /var/www/html/slurm-reports/core_util.html --days 30
    pixi run cli visualize --metric user-distribution --output /var/www/html/slurm-reports/users.html --days 30
    pixi run cli visualize --metric peak-hours --output /var/www/html/slurm-reports/peak_times.html --days 30

    # 3. Set permissions
    sudo chown www-data:www-data /var/www/html/slurm-reports/*.html
    sudo chmod 644 /var/www/html/slurm-reports/*.html

**Nginx Configuration**:

.. code-block:: bash

    # Create Nginx config file
    cat > /etc/nginx/sites-available/slurm-reports << 'EOF'
    server {
        listen 80;
        server_name monitoring.yourcluster.local;

        location / {
            root /var/www/html/slurm-reports;
            autoindex on;
            index dashboard.html;
        }
    }
    EOF

    # Enable site
    sudo ln -s /etc/nginx/sites-available/slurm-reports /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx

**User Access**:

.. code-block:: bash

    http://monitoring.yourcluster.local/dashboard.html
    http://monitoring.yourcluster.local/core_util.html

**Automated Daily Updates**:

.. code-block:: bash

    # Add to crontab (update at 9 AM daily)
    0 9 * * * cd /opt/slurm_monitoring && \
      pixi run cli dashboard --output /var/www/html/slurm-reports/dashboard.html --days 30 && \
      pixi run cli visualize --metric core-utilization --output /var/www/html/slurm-reports/core_util.html --days 30 && \
      pixi run cli visualize --metric user-distribution --output /var/www/html/slurm-reports/users.html --days 30 && \
      pixi run cli visualize --metric peak-hours --output /var/www/html/slurm-reports/peak_times.html --days 30 && \
      chown www-data:www-data /var/www/html/slurm-reports/*.html

Option 3: REST API Server (Most Flexible)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Best for**: Programmatic access, custom dashboards, integration with other tools

**Start API Server**:

.. code-block:: bash

    # Development (foreground)
    pixi run api

    # Production (background with systemd - see API Server Process Management section)
    sudo systemctl start slurm-api

**User Access via API**:

.. code-block:: bash

    # Get stats
    curl http://localhost:5000/api/v1/stats?days=30

    # Get users
    curl http://localhost:5000/api/v1/users?days=30

    # Get peak times
    curl http://localhost:5000/api/v1/peak-times?days=7

**Create Custom Web Interface**:

Users can create their own HTML dashboards that query the API. Example:

.. code-block:: html

    <!DOCTYPE html>
    <html>
    <head>
        <title>SLURM Cluster Monitor</title>
    </head>
    <body>
        <h1>Cluster Statistics</h1>
        <div id="stats"></div>

        <script>
            fetch('http://localhost:5000/api/v1/stats?days=30')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('stats').innerHTML = 
                        'Core Hours: ' + data.utilization.total_core_hours;
                });
        </script>
    </body>
    </html>

Option 4: Quick HTTP Server (Testing/Demo)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Best for**: Quick sharing, temporary access, testing

.. code-block:: bash

    # Generate report
    pixi run cli dashboard --output dashboard.html --days 30

    # Start simple HTTP server (Python)
    python -m http.server 8000

    # Start simple HTTP server (Ruby)
    ruby -run -ehttpd . -p8000

    # Access from another machine
    http://<YOUR_IP>:8000/dashboard.html

**Automating Report Index**:

Create an HTML index to list available reports:

.. code-block:: bash

    cat > /var/www/html/slurm-reports/index.html << 'EOF'
    <!DOCTYPE html>
    <html>
    <head>
        <title>SLURM Cluster Reports</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; }
            .report { 
                background: #f5f5f5; 
                padding: 10px; 
                margin: 10px 0; 
                border-radius: 5px;
            }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>SLURM Cluster Monitoring Reports</h1>
        <p>Last updated: <span id="timestamp"></span></p>
        
        <div class="report">
            <h2>📊 Main Dashboard</h2>
            <p><a href="dashboard.html">View Dashboard</a></p>
            <p>Complete overview of cluster utilization, peak times, and job statistics.</p>
        </div>

        <div class="report">
            <h2>📈 Core Utilization</h2>
            <p><a href="core_util.html">View Chart</a></p>
            <p>Hourly and daily core utilization patterns.</p>
        </div>

        <div class="report">
            <h2>👥 User Distribution</h2>
            <p><a href="users.html">View Chart</a></p>
            <p>Resource usage breakdown by user.</p>
        </div>

        <div class="report">
            <h2>⏰ Peak Times</h2>
            <p><a href="peak_times.html">View Chart</a></p>
            <p>Identify peak usage hours and patterns.</p>
        </div>

        <script>
            document.getElementById('timestamp').textContent = new Date().toLocaleString();
        </script>
    </body>
    </html>
    EOF

Recommended Workflow for Team Sharing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For most teams, **combine methods**:

1. **Daily automated reports** → Web server (Option 2)
2. **Real-time API access** → REST API Server (Option 3)
3. **Backup/archive** → Shared folder weekly

.. code-block:: bash

    # 1. Generate and publish reports daily at 9 AM
    0 9 * * * cd /opt/slurm_monitoring && pixi run cli dashboard --output /var/www/html/slurm-reports/dashboard.html --days 30

    # 2. Archive reports weekly
    0 0 * * 0 tar -czf /backups/slurm-reports-$(date +\%Y\%m\%d).tar.gz /var/www/html/slurm-reports/

    # 3. Keep API running for on-demand queries
    # (systemd service - see API Server Process Management section)

Users access via:

- **For dashboards**: ``http://monitoring.cluster.local/slurm-reports/``
- **For live data**: API endpoints at ``http://monitoring.cluster.local/api/v1/``

Monitoring and Alerting
-----------------------

Health Checks
^^^^^^^^^^^^^

Monitor the API endpoint:

.. code-block:: bash

    # Using curl
    curl -f http://localhost:5000/api/v1/health || systemctl restart slurm-api

    # Using Nagios/Icinga
    check_http -H localhost -p 5000 -u /api/v1/health

Log Monitoring
^^^^^^^^^^^^^^

Watch for errors:

.. code-block:: bash

    # On systemd systems
    journalctl -u slurm-api -f

    # On other systems
    tail -f /var/log/slurm-api.log

Metrics Collection
^^^^^^^^^^^^^^^^^^

Integrate with Prometheus:

.. code-block:: bash

    # In your monitoring script
    core_hours=$(curl -s http://localhost:5000/api/v1/stats | jq '.utilization.total_core_hours')
    echo "slurm_core_hours_total $core_hours" | curl -X POST -d @- http://prometheus:9091/metrics/job/slurm

Troubleshooting
---------------

SLURM Commands Not Available
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptom**: "sacct command not found"

**Solution**:

.. code-block:: bash

    # Verify SLURM is installed
    which sacct

    # If not found, install SLURM client
    # On Ubuntu/Debian
    apt-get install slurm-client

    # On CentOS/RHEL
    yum install slurm

API Server Won't Start
^^^^^^^^^^^^^^^^^^^^^^

**Symptom**: "Address already in use" on port 5000

**Solutions**:

.. code-block:: bash

    # Check what's using the port
    lsof -i :5000

    # Kill existing process
    kill -9 <PID>

    # Or use different port in ~/.slurm_config.yaml
    echo "api: { port: 5001 }" >> ~/.slurm_config.yaml

Slow Data Collection
^^^^^^^^^^^^^^^^^^^^

**Symptom**: Commands taking >30 seconds

**Solutions**:

.. code-block:: bash

    # Increase timeout in ~/.slurm_config.yaml
    slurm:
      command_timeout: 60

    # Reduce lookback period
    pixi run cli stats --days 7  # Instead of 30

    # Check SLURM accounting database health
    sacct --version
    mkdir -p /var/spool/slurm/slurmd  # Ensure cache dir exists

No Data Available
^^^^^^^^^^^^^^^^^

**Symptom**: "No data available" or empty results

**Solutions**:

.. code-block:: bash

    # Check SLURM accounting is working
    sacct -a --format=JobID | wc -l

    # Verify cluster has run jobs
    sinfo   # Check if nodes exist
    squeue  # Check for running jobs

    # Check data lookback isn't too short
    pixi run cli stats --days 1

Performance Tuning
------------------

Optimize Data Collection
^^^^^^^^^^^^^^^^^^^^^^^^

#. **Cache Results**: Save JSON output to avoid repeated queries
#. **Reduce Lookback**: Use smaller time windows when possible
#. **Filter by User**: Analyze specific users instead of whole cluster
#. **Batch Processing**: Process daily instead of monthly for large clusters

Example Cron Schedule
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Lightweight hourly check
    0 * * * * pixi run cli stats --days 1 --output /tmp/hourly.json

    # Heavy weekly deep analysis
    0 2 * * 0 pixi run cli dashboard --days 30 --output /var/www/reports/weekly.html

    # User report twice daily
    0 6,18 * * * pixi run cli users --days 7 --output /var/log/slurm-stats/users.csv

Security Considerations
-----------------------

#. **Run as Dedicated User**: Create a `slurm` system user to run the service
#. **Restrict API Access**: Use firewall rules or reverse proxy authentication
#. **File Permissions**: Ensure output directories are readable only by authorized users
#. **SLURM Cluster Security**: Use SLURM's own security features (munge authentication)
#. **TLS for API**: Use reverse proxy with SSL certificates in production
#. **Credential Management**: Never hardcode usernames/passwords; use SLURM authentication

Example Users and Permissions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Create dedicated user
    useradd -r -s /bin/bash slurm-monitoring

    # Set permissions
    chown slurm-monitoring:slurm-monitoring /opt/slurm_monitoring
    chmod 750 /opt/slurm_monitoring
    chown slurm-monitoring:slurm-monitoring /var/log/slurm-stats
    chmod 750 /var/log/slurm-stats

Disaster Recovery
-----------------

Backup Important Data
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # Backup configuration
    tar -czf slurm-config-backup.tar.gz ~/.slurm_config.yaml

    # Backup reports
    tar -czf slurm-reports-backup.tar.gz /var/www/reports/

    # Add to cron (weekly)
    0 3 * * 0 tar -czf /backups/slurm-reports-$(date +\%Y\%m\%d).tar.gz /var/www/reports/

Rollback Procedures
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    # If API won't start
    systemctl stop slurm-api
    systemctl status slurm-api

    # Check recent changes
    git log --oneline -10

    # Rollback to previous version
    git checkout <previous-commit>
    systemctl start slurm-api
