"""REST API server for SLURM statistics"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import logging

from ..collector import SlurmCollector
from ..analyzer import ClusterAnalyzer
from ..config import get_config

logger = logging.getLogger(__name__)


def create_app(config=None):
    """Create and configure Flask app"""
    app = Flask(__name__)
    CORS(app)

    if config:
        app.config.update(config)

    config_obj = get_config()
    app.config["SLURM_CONFIG"] = config_obj

    register_routes(app)
    return app


def register_routes(app):
    """Register API routes"""

    @app.route("/api/v1/health", methods=["GET"])
    def health():
        """Health check endpoint"""
        return jsonify({"status": "healthy"})

    @app.route("/api/v1/stats", methods=["GET"])
    def get_stats():
        """Get overall cluster statistics"""
        try:
            days = request.args.get("days", default=30, type=int)

            collector = SlurmCollector()
            jobs = collector.get_job_history(days=days)

            if jobs.empty:
                return jsonify({"error": "No data available"}), 404

            analyzer = ClusterAnalyzer(jobs)
            return jsonify(analyzer.get_summary())

        except Exception as e:
            logger.exception(e)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/v1/users", methods=["GET"])
    def get_users():
        """Get per-user statistics"""
        try:
            days = request.args.get("days", default=30, type=int)

            collector = SlurmCollector()
            jobs = collector.get_job_history(days=days)

            if jobs.empty:
                return jsonify({"error": "No data available"}), 404

            analyzer = ClusterAnalyzer(jobs)
            return jsonify(analyzer.breakdown_by_user())

        except Exception as e:
            logger.exception(e)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/v1/utilization", methods=["GET"])
    def get_utilization():
        """Get core utilization statistics"""
        try:
            days = request.args.get("days", default=30, type=int)

            collector = SlurmCollector()
            jobs = collector.get_job_history(days=days)

            if jobs.empty:
                return jsonify({"error": "No data available"}), 404

            analyzer = ClusterAnalyzer(jobs)
            return jsonify(analyzer.compute_core_utilization())

        except Exception as e:
            logger.exception(e)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/v1/peak-times", methods=["GET"])
    def get_peak_times():
        """Get peak usage times"""
        try:
            days = request.args.get("days", default=30, type=int)

            collector = SlurmCollector()
            jobs = collector.get_job_history(days=days)

            if jobs.empty:
                return jsonify({"error": "No data available"}), 404

            analyzer = ClusterAnalyzer(jobs)
            return jsonify(analyzer.identify_peak_times())

        except Exception as e:
            logger.exception(e)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/v1/job-stats", methods=["GET"])
    def get_job_stats():
        """Get job duration and frequency statistics"""
        try:
            days = request.args.get("days", default=30, type=int)

            collector = SlurmCollector()
            jobs = collector.get_job_history(days=days)

            if jobs.empty:
                return jsonify({"error": "No data available"}), 404

            analyzer = ClusterAnalyzer(jobs)
            return jsonify(
                {
                    "duration": analyzer.compute_job_duration_stats(),
                    "frequency": analyzer.compute_job_frequency(),
                }
            )

        except Exception as e:
            logger.exception(e)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/v1/cluster-state", methods=["GET"])
    def get_cluster_state():
        """Get current cluster state"""
        try:
            collector = SlurmCollector()
            state = collector.get_cluster_state()

            return jsonify(
                {
                    "state": state.to_dict("records") if not state.empty else [],
                    "summary": collector.sinfo.get_summary(),
                }
            )

        except Exception as e:
            logger.exception(e)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/v1/running-jobs", methods=["GET"])
    def get_running_jobs():
        """Get currently running jobs"""
        try:
            collector = SlurmCollector()
            running = collector.get_running_jobs()

            return jsonify(
                {
                    "jobs": running.to_dict("records") if not running.empty else [],
                    "summary": collector.squeue.get_summary(),
                }
            )

        except Exception as e:
            logger.exception(e)
            return jsonify({"error": str(e)}), 500


def main():
    """Run the API server"""
    import argparse

    parser = argparse.ArgumentParser(description="Run the SLURM monitoring API server")
    parser.add_argument("--port", type=int, help="Port (default: api.port from config, else 5000)")
    parser.add_argument("--host", help="Address to bind (default: api.host from config)")
    args = parser.parse_args()

    config = get_config()
    api_config = config.get("api", {})

    app = create_app()
    app.run(
        host=args.host or api_config.get("host", "0.0.0.0"),
        port=args.port or api_config.get("port", 5000),
        debug=api_config.get("debug", False),
    )


if __name__ == "__main__":
    main()
