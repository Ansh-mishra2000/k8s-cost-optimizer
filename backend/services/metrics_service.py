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
        recommendation
    ):

        cls.monthly_cpu_cost.set(
            recommendation[
                "monthly_cpu_cost_usd"
            ]
        )

        cls.monthly_memory_cost.set(
            recommendation[
                "monthly_memory_cost_usd"
            ]
        )

        cls.monthly_total_cost.set(
            recommendation[
                "monthly_total_cost_usd"
            ]
        )

        cls.monthly_savings.set(
            recommendation[
                "monthly_total_savings_usd"
            ]
        )