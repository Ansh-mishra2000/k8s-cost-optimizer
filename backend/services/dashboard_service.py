import io
import csv
import logging
from sqlalchemy import text
from fastapi import HTTPException

from database.db import get_db_session

logger = logging.getLogger(__name__)


class DashboardService:

    def get_dashboard_summary(self):
        """Aggregate summary metrics across all latest deployment recommendations."""
        query = text("""
            WITH latest AS (
                SELECT DISTINCT ON (deployment_name)
                    deployment_name,
                    namespace,
                    requested_cpu,
                    actual_cpu,
                    requested_memory_mib,
                    actual_memory_mib,
                    monthly_total_cost_usd,
                    monthly_total_savings_usd,
                    timestamp
                FROM recommendations
                ORDER BY deployment_name, timestamp DESC
            )
            SELECT
                COUNT(*) AS total_deployments,
                COALESCE(SUM(monthly_total_cost_usd), 0) AS total_monthly_cost,
                COALESCE(SUM(monthly_total_savings_usd), 0) AS total_monthly_savings,
                (SELECT deployment_name FROM latest ORDER BY actual_cpu DESC LIMIT 1) AS highest_cpu_deployment,
                (SELECT deployment_name FROM latest ORDER BY actual_memory_mib DESC LIMIT 1) AS highest_memory_deployment,
                (SELECT deployment_name FROM latest ORDER BY monthly_total_savings_usd DESC LIMIT 1) AS largest_saving_deployment
            FROM latest;
        """)

        try:
            with get_db_session() as db:
                result = db.execute(query).mappings().first()

            if not result or result["total_deployments"] == 0:
                return {
                    "total_deployments": 0,
                    "total_monthly_cost": 0.0,
                    "total_monthly_savings": 0.0,
                    "highest_cpu_deployment": None,
                    "highest_memory_deployment": None,
                    "largest_saving_deployment": None,
                }

            return {
                "total_deployments": result["total_deployments"],
                "total_monthly_cost": round(float(result["total_monthly_cost"]), 2),
                "total_monthly_savings": round(float(result["total_monthly_savings"]), 2),
                "highest_cpu_deployment": result["highest_cpu_deployment"],
                "highest_memory_deployment": result["highest_memory_deployment"],
                "largest_saving_deployment": result["largest_saving_deployment"],
            }
        except Exception as e:
            logger.error("Error in get_dashboard_summary: %s", e)
            raise HTTPException(status_code=500, detail=f"Dashboard summary failed: {str(e)}")

    def get_deployment_details(self, deployment_name: str):
        """Fetch the latest recommendation details for a single deployment."""
        query = text("""
            SELECT *
            FROM recommendations
            WHERE deployment_name = :deployment_name
            ORDER BY timestamp DESC
            LIMIT 1;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query, {"deployment_name": deployment_name}).mappings().first()

            if result is None:
                return {"error": f"Deployment '{deployment_name}' not found."}
            return dict(result)
        except Exception as e:
            logger.error("Error in get_deployment_details: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_cpu_trend(self, deployment_name: str):
        """Fetch historical CPU usage and recommendation trend."""
        query = text("""
            SELECT
                timestamp,
                actual_cpu,
                avg_cpu_24h,
                peak_cpu_24h
            FROM recommendations
            WHERE deployment_name = :deployment_name
            ORDER BY timestamp ASC;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query, {"deployment_name": deployment_name}).mappings().all()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Error in get_cpu_trend: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_memory_trend(self, deployment_name: str):
        """Fetch historical memory usage trend."""
        query = text("""
            SELECT
                timestamp,
                actual_memory_mib,
                recommended_memory_mib,
                requested_memory_mib
            FROM recommendations
            WHERE deployment_name = :deployment_name
            ORDER BY timestamp ASC;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query, {"deployment_name": deployment_name}).mappings().all()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Error in get_memory_trend: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_cost_trend(self, deployment_name: str):
        """Fetch historical cost and optimized cost trend."""
        query = text("""
            SELECT
                timestamp,
                monthly_total_cost_usd,
                optimized_monthly_total_cost_usd
            FROM recommendations
            WHERE deployment_name = :deployment_name
            ORDER BY timestamp ASC;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query, {"deployment_name": deployment_name}).mappings().all()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Error in get_cost_trend: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_savings_trend(self, deployment_name: str):
        """Fetch historical savings trend."""
        query = text("""
            SELECT
                timestamp,
                monthly_total_savings_usd
            FROM recommendations
            WHERE deployment_name = :deployment_name
            ORDER BY timestamp ASC;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query, {"deployment_name": deployment_name}).mappings().all()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Error in get_savings_trend: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_top_savings(self):
        """List top 5 deployments with the highest monthly savings opportunity."""
        query = text("""
            WITH latest AS (
                SELECT DISTINCT ON (deployment_name)
                    deployment_name,
                    namespace,
                    monthly_total_cost_usd,
                    optimized_monthly_total_cost_usd,
                    monthly_total_savings_usd,
                    timestamp
                FROM recommendations
                ORDER BY deployment_name, timestamp DESC
            )
            SELECT *
            FROM latest
            WHERE monthly_total_savings_usd > 0
            ORDER BY monthly_total_savings_usd DESC
            LIMIT 5;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query).mappings().all()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Error in get_top_savings: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_top_cost(self):
        """List top 5 most expensive deployments."""
        query = text("""
            WITH latest AS (
                SELECT DISTINCT ON (deployment_name)
                    deployment_name,
                    namespace,
                    monthly_total_cost_usd,
                    optimized_monthly_total_cost_usd,
                    monthly_total_savings_usd,
                    timestamp
                FROM recommendations
                ORDER BY deployment_name, timestamp DESC
            )
            SELECT *
            FROM latest
            ORDER BY monthly_total_cost_usd DESC
            LIMIT 5;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query).mappings().all()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Error in get_top_cost: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_overprovisioned(self):
        """List deployments where requested resources significantly exceed actual utilization."""
        query = text("""
            WITH latest AS (
                SELECT DISTINCT ON (deployment_name)
                    deployment_name,
                    namespace,
                    requested_cpu,
                    actual_cpu,
                    recommended_cpu,
                    requested_memory_mib,
                    actual_memory_mib,
                    recommended_memory_mib,
                    monthly_total_savings_usd,
                    timestamp
                FROM recommendations
                ORDER BY deployment_name, timestamp DESC
            )
            SELECT *
            FROM latest
            WHERE requested_cpu > recommended_cpu OR requested_memory_mib > recommended_memory_mib
            ORDER BY monthly_total_savings_usd DESC;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query).mappings().all()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Error in get_overprovisioned: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_underprovisioned(self):
        """List deployments running close to or above requests (risk of throttling/OOM)."""
        query = text("""
            WITH latest AS (
                SELECT DISTINCT ON (deployment_name)
                    deployment_name,
                    namespace,
                    requested_cpu,
                    actual_cpu,
                    recommended_cpu,
                    requested_memory_mib,
                    actual_memory_mib,
                    recommended_memory_mib,
                    timestamp
                FROM recommendations
                ORDER BY deployment_name, timestamp DESC
            )
            SELECT *
            FROM latest
            WHERE actual_cpu > requested_cpu OR actual_memory_mib > requested_memory_mib
            ORDER BY actual_cpu DESC;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query).mappings().all()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Error in get_underprovisioned: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_recommendation_history(self, deployment_name: str):
        """Fetch all historical recommendations for a deployment."""
        query = text("""
            SELECT *
            FROM recommendations
            WHERE deployment_name = :deployment_name
            ORDER BY timestamp DESC;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query, {"deployment_name": deployment_name}).mappings().all()
            return [dict(row) for row in result]
        except Exception as e:
            logger.error("Error in get_recommendation_history: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_cluster_utilization(self):
        """Calculate cluster-level total allocated vs actual utilized resources."""
        query = text("""
            WITH latest AS (
                SELECT DISTINCT ON (deployment_name)
                    requested_cpu,
                    actual_cpu,
                    requested_memory_mib,
                    actual_memory_mib
                FROM recommendations
                ORDER BY deployment_name, timestamp DESC
            )
            SELECT
                COALESCE(SUM(requested_cpu), 0) AS total_requested_cpu,
                COALESCE(SUM(actual_cpu), 0) AS total_actual_cpu,
                COALESCE(SUM(requested_memory_mib), 0) AS total_requested_memory_mib,
                COALESCE(SUM(actual_memory_mib), 0) AS total_actual_memory_mib
            FROM latest;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query).mappings().first()

            if not result:
                return {
                    "total_requested_cpu": 0,
                    "total_actual_cpu": 0,
                    "cpu_utilization_percentage": 0,
                    "total_requested_memory_mib": 0,
                    "total_actual_memory_mib": 0,
                    "memory_utilization_percentage": 0
                }

            req_cpu = float(result["total_requested_cpu"])
            act_cpu = float(result["total_actual_cpu"])
            cpu_pct = round((act_cpu / req_cpu * 100), 2) if req_cpu > 0 else 0.0

            req_mem = float(result["total_requested_memory_mib"])
            act_mem = float(result["total_actual_memory_mib"])
            mem_pct = round((act_mem / req_mem * 100), 2) if req_mem > 0 else 0.0

            return {
                "total_requested_cpu": req_cpu,
                "total_actual_cpu": round(act_cpu, 4),
                "cpu_utilization_percentage": cpu_pct,
                "total_requested_memory_mib": req_mem,
                "total_actual_memory_mib": round(act_mem, 2),
                "memory_utilization_percentage": mem_pct
            }
        except Exception as e:
            logger.error("Error in get_cluster_utilization: %s", e)
            raise HTTPException(status_code=500, detail=str(e))

    def export_recommendations_csv(self):
        """Export all recommendations from the database as a CSV string."""
        query = text("""
            SELECT *
            FROM recommendations
            ORDER BY timestamp DESC;
        """)
        try:
            with get_db_session() as db:
                result = db.execute(query).mappings().all()

            if not result:
                return "No recommendations found."

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=result[0].keys())
            writer.writeheader()
            for row in result:
                writer.writerow(dict(row))

            return output.getvalue()
        except Exception as e:
            logger.error("Error in export_recommendations_csv: %s", e)
            raise HTTPException(status_code=500, detail=str(e))