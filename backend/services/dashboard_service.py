import io
import csv
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

    def get_cpu_trend(
        self,
        deployment_name: str
    ):

        try:

            query = text("""

                SELECT

                    timestamp,

                    actual_cpu,

                    avg_cpu_24h,

                    peak_cpu_24h

                FROM recommendations

                WHERE deployment_name = :deployment_name

                ORDER BY timestamp;

            """)

            result = self.db.execute(

                query,

                {

                    "deployment_name": deployment_name

                }

            ).mappings().all()

            return [

                dict(row)

                for row in result

            ]

        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=str(e)

            )

        finally:

            self.db.close()

    def get_memory_trend(
        self,
        deployment_name: str
    ):

        try:

            query = text("""

                SELECT

                    timestamp,

                    actual_memory_mib,

                    recommended_memory_mib

                FROM recommendations

                WHERE deployment_name = :deployment_name

                ORDER BY timestamp;

            """)

            result = self.db.execute(

                query,

                {

                    "deployment_name": deployment_name

                }

            ).mappings().all()

            return [

                dict(row)

                for row in result

            ]

        except Exception as e:

            raise HTTPException(

                status_code=500,

                detail=str(e)

            )

        finally:

            self.db.close()

    def get_cost_trend(
        self,
        deployment_name: str
    ):

        query = text("""

            SELECT

                timestamp,

                monthly_total_cost_usd,

                optimized_monthly_total_cost_usd

            FROM recommendations

            WHERE deployment_name = :deployment_name

            ORDER BY timestamp;

        """)

        result = self.db.execute(

            query,

            {

                "deployment_name": deployment_name

            }

        ).mappings().all()

        return [

            dict(row)

            for row in result

        ]
    def get_savings_trend(
            self,
            deployment_name: str
        ):

            query = text("""

                SELECT

                    timestamp,

                    monthly_total_savings_usd

                FROM recommendations

                WHERE deployment_name = :deployment_name

                ORDER BY timestamp;

            """)

            result = self.db.execute(

                query,

                {

                    "deployment_name": deployment_name

                }

            ).mappings().all()

            return [

                dict(row)

                for row in result

            ]
    def get_top_savings(self):

        query = text("""

            WITH latest AS (

                SELECT DISTINCT ON (deployment_name)

                    deployment_name,

                    monthly_total_savings_usd,

                    timestamp

                FROM recommendations

                ORDER BY deployment_name, timestamp DESC

            )

            SELECT

                deployment_name,

                monthly_total_savings_usd

            FROM latest

            ORDER BY monthly_total_savings_usd DESC;

        """)

        result = self.db.execute(query).mappings().all()

        return [

            dict(row)

            for row in result

        ]
    
    def get_top_cost(self):

        query = text("""

            WITH latest AS (

                SELECT DISTINCT ON (deployment_name)

                    deployment_name,

                    monthly_total_cost_usd,

                    timestamp

                FROM recommendations

                ORDER BY deployment_name, timestamp DESC

            )

            SELECT

                deployment_name,

                monthly_total_cost_usd

            FROM latest

            ORDER BY monthly_total_cost_usd DESC;

        """)

        result = self.db.execute(query).mappings().all()

        return [

            dict(row)

            for row in result

        ]
    def get_overprovisioned(self):

        OVERPROVISION_THRESHOLD = 20

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

            SELECT

                deployment_name,

                namespace,

                requested_cpu,

                actual_cpu,

                ROUND(
                    (
                        (
                            (requested_cpu - actual_cpu)
                            / NULLIF(requested_cpu, 0)
                        ) * 100
                    )::numeric,
                    2
                ) AS cpu_waste_percent,

                recommended_cpu,

                requested_memory_mib,

                actual_memory_mib,

                ROUND(
                    (
                        (
                            (requested_memory_mib - actual_memory_mib)
                            / NULLIF(requested_memory_mib, 0)
                        ) * 100
                    )::numeric,
                    2
                ) AS memory_waste_percent,

                recommended_memory_mib,

                monthly_total_savings_usd

            FROM latest

            WHERE

                (
                    (
                        (requested_cpu - actual_cpu)
                        / NULLIF(requested_cpu, 0)
                    ) * 100
                ) >= :threshold

                OR

                (
                    (
                        (requested_memory_mib - actual_memory_mib)
                        / NULLIF(requested_memory_mib, 0)
                    ) * 100
                ) >= :threshold

            ORDER BY

                monthly_total_savings_usd DESC;

        """)

        result = self.db.execute(
            query,
            {"threshold": OVERPROVISION_THRESHOLD}
        ).mappings().all()

        response = []

        for row in result:

            item = dict(row)

            item["overprovisioned_by"] = {

                "cpu": {

                    "overprovisioned":
                        item["cpu_waste_percent"] >= OVERPROVISION_THRESHOLD,

                    "waste_percent":
                        item["cpu_waste_percent"]

                },

                "memory": {

                    "overprovisioned":
                        item["memory_waste_percent"] >= OVERPROVISION_THRESHOLD,

                    "waste_percent":
                        item["memory_waste_percent"]

                }

            }

            response.append(item)

        return response
    def get_underprovisioned(self):

        UNDERPROVISION_THRESHOLD = 20

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

            SELECT

                deployment_name,

                namespace,

                requested_cpu,

                actual_cpu,

                ROUND(
                    (
                        (
                            (actual_cpu - requested_cpu)
                            / NULLIF(requested_cpu,0)
                        ) * 100
                    )::numeric,
                    2
                ) AS cpu_shortage_percent,

                recommended_cpu,

                requested_memory_mib,

                actual_memory_mib,

                ROUND(
                    (
                        (
                            (actual_memory_mib - requested_memory_mib)
                            / NULLIF(requested_memory_mib,0)
                        ) *100
                    )::numeric,
                    2
                ) AS memory_shortage_percent,

                recommended_memory_mib,

                monthly_total_savings_usd

            FROM latest

            WHERE

                (
                    (
                        (actual_cpu-requested_cpu)
                        /NULLIF(requested_cpu,0)
                    )*100
                ) >= :threshold

                OR

                (
                    (
                        (actual_memory_mib-requested_memory_mib)
                        /NULLIF(requested_memory_mib,0)
                    )*100
                ) >= :threshold

            ORDER BY

                cpu_shortage_percent DESC;

        """)

        result = self.db.execute(
            query,
            {"threshold": UNDERPROVISION_THRESHOLD}
        ).mappings().all()

        response = []

        for row in result:

            item = dict(row)

            item["underprovisioned_by"] = {

                "cpu": {

                    "underprovisioned":
                        item["cpu_shortage_percent"] >= UNDERPROVISION_THRESHOLD,

                    "shortage_percent":
                        item["cpu_shortage_percent"]

                },

                "memory": {

                    "underprovisioned":
                        item["memory_shortage_percent"] >= UNDERPROVISION_THRESHOLD,

                    "shortage_percent":
                        item["memory_shortage_percent"]

                }

            }

            response.append(item)

        return response
    

    def get_dashboard_summary(self):

        OVERPROVISION_THRESHOLD = 20
        UNDERPROVISION_THRESHOLD = 20

        query = text("""

            WITH latest AS (

                SELECT DISTINCT ON (deployment_name)

                    deployment_name,

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

                ROUND(
                    SUM(monthly_total_cost_usd)::numeric,
                    2
                ) AS monthly_total_cost_usd,

                ROUND(

                    SUM(

                        CASE

                            WHEN monthly_total_savings_usd > 0

                            THEN monthly_total_savings_usd

                            ELSE 0

                        END

                    )::numeric,

                    2

                ) AS potential_monthly_savings_usd,

                COUNT(

                    CASE

                        WHEN

                            (

                                (
                                    (requested_cpu-actual_cpu)

                                    /NULLIF(requested_cpu,0)

                                )*100

                            ) >= :over_threshold

                        OR

                            (

                                (
                                    (requested_memory_mib-actual_memory_mib)

                                    /NULLIF(requested_memory_mib,0)

                                )*100

                            ) >= :over_threshold

                        THEN 1

                    END

                ) AS overprovisioned_deployments,

                COUNT(

                    CASE

                        WHEN

                            (

                                (
                                    (actual_cpu-requested_cpu)

                                    /NULLIF(requested_cpu,0)

                                )*100

                            ) >= :under_threshold

                        OR

                            (

                                (
                                    (actual_memory_mib-requested_memory_mib)

                                    /NULLIF(requested_memory_mib,0)

                                )*100

                            ) >= :under_threshold

                        THEN 1

                    END

                ) AS underprovisioned_deployments

            FROM latest;

        """)

        summary = self.db.execute(

            query,

            {

                "over_threshold": OVERPROVISION_THRESHOLD,

                "under_threshold": UNDERPROVISION_THRESHOLD

            }

        ).mappings().first()

        response = dict(summary)

        if response["underprovisioned_deployments"] > 0:

            response["cluster_health"] = "Critical"

        elif response["overprovisioned_deployments"] > 0:

            response["cluster_health"] = "Needs Optimization"

        else:

            response["cluster_health"] = "Healthy"

        return response
    def get_recommendation_history(self, deployment_name: str):

        query = text("""

            SELECT

                timestamp,

                requested_cpu,

                actual_cpu,

                recommended_cpu,

                requested_memory_mib,

                actual_memory_mib,

                recommended_memory_mib,

                monthly_total_cost_usd,

                optimized_monthly_total_cost_usd,

                monthly_total_savings_usd

            FROM recommendations

            WHERE deployment_name = :deployment_name

            ORDER BY timestamp DESC

            LIMIT 100;

        """)

        result = self.db.execute(

            query,

            {

                "deployment_name": deployment_name

            }

        ).mappings().all()

        return [dict(row) for row in result]
    
    def get_cluster_utilization(self):

        OVERPROVISION_THRESHOLD = 20
        UNDERPROVISION_THRESHOLD = 20

        query = text("""

            WITH latest AS (

                SELECT DISTINCT ON (deployment_name)

                    deployment_name,
                    requested_cpu,
                    actual_cpu,
                    requested_memory_mib,
                    actual_memory_mib

                FROM recommendations

                ORDER BY deployment_name, timestamp DESC

            )

            SELECT

                ROUND(
                    SUM(requested_cpu)::numeric,
                    2
                ) AS requested_cpu,

                ROUND(
                    SUM(actual_cpu)::numeric,
                    2
                ) AS actual_cpu,

                ROUND(
                    (
                        (
                            SUM(actual_cpu)
                            /
                            NULLIF(SUM(requested_cpu),0)
                        ) * 100
                    )::numeric,
                    2
                ) AS cpu_utilization_percent,

                ROUND(
                    SUM(requested_memory_mib)::numeric,
                    2
                ) AS requested_memory_mib,

                ROUND(
                    SUM(actual_memory_mib)::numeric,
                    2
                ) AS actual_memory_mib,

                ROUND(
                    (
                        (
                            SUM(actual_memory_mib)
                            /
                            NULLIF(SUM(requested_memory_mib),0)
                        ) * 100
                    )::numeric,
                    2
                ) AS memory_utilization_percent,

                COUNT(*) AS total_deployments,

                COUNT(

                    CASE

                        WHEN

                            (

                                (
                                    (requested_cpu-actual_cpu)

                                    / NULLIF(requested_cpu,0)

                                ) * 100

                            ) >= :over_threshold

                        OR

                            (

                                (
                                    (requested_memory_mib-actual_memory_mib)

                                    / NULLIF(requested_memory_mib,0)

                                ) * 100

                            ) >= :over_threshold

                        THEN 1

                    END

                ) AS overprovisioned_deployments,

                COUNT(

                    CASE

                        WHEN

                            (

                                (
                                    (actual_cpu-requested_cpu)

                                    / NULLIF(requested_cpu,0)

                                ) * 100

                            ) >= :under_threshold

                        OR

                            (

                                (
                                    (actual_memory_mib-requested_memory_mib)

                                    / NULLIF(requested_memory_mib,0)

                                ) * 100

                            ) >= :under_threshold

                        THEN 1

                    END

                ) AS underprovisioned_deployments

            FROM latest;

        """)

        result = self.db.execute(

            query,

            {
                "over_threshold": OVERPROVISION_THRESHOLD,
                "under_threshold": UNDERPROVISION_THRESHOLD
            }

        ).mappings().first()

        utilization = dict(result)

        cpu = utilization["cpu_utilization_percent"] or 0
        memory = utilization["memory_utilization_percent"] or 0

        utilization["cost_efficiency_score"] = round(
            (cpu + memory) / 2,
            2
        )

        # -----------------------------
        # Cluster Health Logic
        # -----------------------------

        over = utilization["overprovisioned_deployments"]
        under = utilization["underprovisioned_deployments"]

        if under > 0:

            utilization["cluster_health"] = {

                "status": "critical",

                "label": "Critical",

                "reason": f"{under} deployment(s) are underprovisioned."

            }

        elif over > 0:

            utilization["cluster_health"] = {

                "status": "warning",

                "label": "Needs Optimization",

                "reason": f"{over} deployment(s) are overprovisioned."

            }

        else:

            utilization["cluster_health"] = {

                "status": "healthy",

                "label": "Excellent",

                "reason": "All deployments are correctly provisioned."

            }

        return utilization
    
    def export_recommendations_csv(self):

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

                    monthly_total_cost_usd,

                    optimized_monthly_total_cost_usd,

                    monthly_total_savings_usd,

                    timestamp

                FROM recommendations

                ORDER BY deployment_name, timestamp DESC

            )

            SELECT *

            FROM latest

            ORDER BY deployment_name;

        """)

        rows = self.db.execute(query).mappings().all()

        output = io.StringIO()

        writer = csv.writer(output)

        writer.writerow([

            "Timestamp",

            "Deployment",

            "Namespace",

            "Requested CPU",

            "Actual CPU",

            "Recommended CPU",

            "Requested Memory (MiB)",

            "Actual Memory (MiB)",

            "Recommended Memory (MiB)",

            "Monthly Cost (USD)",

            "Optimized Monthly Cost (USD)",

            "Monthly Savings (USD)"

        ])

        for row in rows:

            writer.writerow([

                row["timestamp"],

                row["deployment_name"],

                row["namespace"],

                row["requested_cpu"],

                row["actual_cpu"],

                row["recommended_cpu"],

                row["requested_memory_mib"],

                row["actual_memory_mib"],

                row["recommended_memory_mib"],

                row["monthly_total_cost_usd"],

                row["optimized_monthly_total_cost_usd"],

                row["monthly_total_savings_usd"]

            ])

        return output.getvalue()