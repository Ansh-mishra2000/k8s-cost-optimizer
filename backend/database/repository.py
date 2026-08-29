import logging
from database.db import get_db_session
from database.models import Recommendation

logger = logging.getLogger(__name__)


class RecommendationRepository:

    @staticmethod
    def save_recommendation(data: dict):
        """Persist a recommendation record into PostgreSQL using a scoped session."""
        try:
            with get_db_session() as db:
                recommendation = Recommendation(
                    deployment_name=data["deployment"],
                    namespace=data.get("namespace", "default"),
                    requested_cpu=data.get("requested_cpu"),
                    actual_cpu=data.get("actual_cpu"),
                    avg_cpu_24h=data.get("avg_cpu_24h"),
                    peak_cpu_24h=data.get("peak_cpu_24h"),
                    recommended_cpu=data.get("recommended_cpu"),
                    requested_memory_mib=data.get("requested_memory_mib"),
                    actual_memory_mib=data.get("actual_memory_mib"),
                    recommended_memory_mib=data.get("recommended_memory_mib"),
                    instance_type=data.get("instance_type"),
                    monthly_total_cost_usd=data.get("monthly_total_cost_usd"),
                    optimized_monthly_total_cost_usd=data.get("optimized_monthly_total_cost_usd"),
                    monthly_total_savings_usd=data.get("monthly_total_savings_usd")
                )
                db.add(recommendation)
                db.commit()
                logger.info("Saved recommendation for %s/%s", data.get("namespace"), data["deployment"])
        except Exception as e:
            logger.error("Failed to save recommendation to DB: %s", e)
            raise