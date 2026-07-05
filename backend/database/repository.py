from database.db import SessionLocal
from database.models import Recommendation


class RecommendationRepository:

    @staticmethod
    def save_recommendation(data):

        db = SessionLocal()

        try:

            recommendation = Recommendation(

                deployment_name=data["deployment"],

                namespace=data.get(
                    "namespace",
                    "default"
                ),

                requested_cpu=data["requested_cpu"],

                actual_cpu=data["actual_cpu"],

                avg_cpu_24h=data["avg_cpu_24h"],

                peak_cpu_24h=data["peak_cpu_24h"],

                recommended_cpu=data["recommended_cpu"],

                requested_memory_mib=data["requested_memory_mib"],

                actual_memory_mib=data["actual_memory_mib"],

                recommended_memory_mib=data["recommended_memory_mib"],

                instance_type=data["instance_type"],

                monthly_total_cost_usd=data[
                    "monthly_total_cost_usd"
                ],

                optimized_monthly_total_cost_usd=data[
                    "optimized_monthly_total_cost_usd"
                ],

                monthly_total_savings_usd=data[
                    "monthly_total_savings_usd"
                ]

            )

            db.add(recommendation)

            db.commit()

        finally:

            db.close()