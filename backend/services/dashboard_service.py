from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi import HTTPException

from database.db import SessionLocal

class DashboardService:

    def __init__(self):

        self.db: Session = SessionLocal()

    def get_dashboard_summary(self):

        try:
            query = text("""
            WITH latest AS (

            SELECT DISTINCT ON (deployment_name)
                *
            FROM recommendations
            ORDER BY deployment_name, timestamp DESC

        )

        SELECT
            COUNT(*) AS total_deployments,

            SUM(monthly_total_cost_usd) AS total_monthly_cost,

            SUM(monthly_total_savings_usd) AS total_monthly_savings,

            (
                SELECT deployment_name
                FROM latest
                ORDER BY actual_cpu DESC
                LIMIT 1
            ) AS highest_cpu_deployment,

            (
                SELECT deployment_name
                FROM latest
                ORDER BY actual_memory_mib DESC
                LIMIT 1
            ) AS highest_memory_deployment,

            (
                SELECT deployment_name
                FROM latest
                ORDER BY monthly_total_savings_usd DESC
                LIMIT 1
            ) AS largest_saving_deployment

        FROM latest;
        """ )

            result = self.db.execute(query).mappings().first()

            if result is None:
                return {
                    "total_deployments": 0,
                    "total_monthly_cost": 0,
                    "total_monthly_savings": 0,
                    "highest_cpu_deployment": None,
                    "highest_memory_deployment": None,
                    "largest_saving_deployment": None,
                }

            return {
                "total_deployments": result["total_deployments"],
                "total_monthly_cost": round(result["total_monthly_cost"], 2),
                "total_monthly_savings": round(result["total_monthly_savings"], 2),
                "highest_cpu_deployment": result["highest_cpu_deployment"],
                "highest_memory_deployment": result["highest_memory_deployment"],
                "largest_saving_deployment": result["largest_saving_deployment"],
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Dashboard summary failed: {str(e)}"
            )
        
        finally:
            self.db.close()

    def get_deployment_details(
        self,
        deployment_name: str
    ):

        try:

            query = text("""

                SELECT *

                FROM recommendations

                WHERE deployment_name = :deployment_name

                ORDER BY timestamp DESC

                LIMIT 1;

            """)

            result = self.db.execute(

                query,

                {

                    "deployment_name": deployment_name

                }

            ).mappings().first()

            if result is None:

                return {

                    "error":
                        "Deployment not found."

                }

            return dict(result)

        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=str(e)

            )

        finally:

            self.db.close()