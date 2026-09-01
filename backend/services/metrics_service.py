# services/metrics_service.py
from prometheus_client import Gauge


class MetricsService:

    monthly_cpu_cost = Gauge(
        "k8s_monthly_cpu_cost",
        "Monthly CPU Cost in USD"
    )

    monthly_memory_cost = Gauge(
        "k8s_monthly_memory_cost",
        "Monthly Memory Cost in USD"
    )

    monthly_total_cost = Gauge(
        "k8s_monthly_total_cost",
        "Monthly Total Cost in USD"
    )

    monthly_savings = Gauge(
        "k8s_monthly_savings",
        "Monthly Savings in USD"
    )

    @classmethod
    def update_metrics(
        cls,
        recommendation: dict
    ):
        if not recommendation or not isinstance(recommendation, dict):
            return

        cost = recommendation.get("cost_breakdown_usd", {})

        cpu_cost = cost.get(
            "monthly_cpu_cost",
            recommendation.get("monthly_cpu_cost_usd", 0.0)
        )
        mem_cost = cost.get(
            "monthly_memory_cost",
            recommendation.get("monthly_memory_cost_usd", 0.0)
        )
        total_cost = cost.get(
            "current_monthly_total",
            recommendation.get("monthly_total_cost_usd", 0.0)
        )
        savings = cost.get(
            "monthly_savings",
            recommendation.get("monthly_total_savings_usd", 0.0)
        )

        cls.monthly_cpu_cost.set(cpu_cost)
        cls.monthly_memory_cost.set(mem_cost)
        cls.monthly_total_cost.set(total_cost)
        cls.monthly_savings.set(savings)