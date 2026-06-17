from services.kubernetes_service import KubernetesService
from services.prometheus_service import PrometheusService
from services.analyzer import Analyzer
from kubernetes.client.exceptions import ApiException
from services.aws_service import AWSService
from services.cost_analyzer import CostAnalyzer


class RecommendationService:

    def get_recommendation(
        self,
        deployment_name
    ):

        k8s = KubernetesService()
        prom = PrometheusService()
        aws = AWSService()

        try:

            resources = k8s.get_deployment_resources(
                deployment_name
            )

        except ApiException:

            return {

                "error":

                f"Deployment "
                f"'{deployment_name}' "
                f"not found."
            }

        # =====================
        # CPU Metrics
        # =====================

        try:

            cpu_metrics = prom.get_cpu_usage(
                deployment_name
            )

        except Exception:

            return {

                "error":

                "Unable to connect to Prometheus."
            }

        if not cpu_metrics:

            return {

                "error":

                f"No CPU metrics found "
                f"for deployment "
                f"'{deployment_name}'."
            }

        actual_cpu = float(
            cpu_metrics[0]["value"][1]
        )

        requested_cpu = resources[
            "cpu_request"
        ]

        if isinstance(requested_cpu, str):

            if requested_cpu.endswith("m"):

                requested_cpu = (
                    float(
                        requested_cpu.replace(
                            "m",
                            ""
                        )
                    ) / 1000
                )

            else:

                requested_cpu = float(
                    requested_cpu
                )

        requested_cpu *= resources[
            "replicas"
        ]

        cpu_waste = Analyzer.calculate_cpu_waste(
            requested_cpu,
            actual_cpu
        )

        recommended_cpu = Analyzer.recommend_cpu(
            requested_cpu,
            actual_cpu
        )

        cpu_reason = (

            f"Observed CPU usage was "
            f"{round(actual_cpu, 2)} cores "
            f"against a requested allocation of "
            f"{round(requested_cpu, 2)} cores. "
            f"The recommendation adds a 20% "
            f"safety buffer to the observed usage."
        )

        # =====================
        # CPU Cost Calculations
        # =====================

        node_info = k8s.get_node_capacity(
            deployment_name
        )

        instance_type = aws.get_instance_type(
            node_info["instance_id"]
        )

        hourly_price = aws.get_hourly_price(
            instance_type
        )

        monthly_cpu_cost = (
            CostAnalyzer.calculate_monthly_cpu_cost(
                cpu_allocation=requested_cpu,
                node_cpu_capacity=node_info[
                    "cpu_capacity"
                ],
                node_hourly_price=hourly_price
            )
        )

        optimized_monthly_cpu_cost = (
            CostAnalyzer.calculate_monthly_cpu_cost(
                cpu_allocation=recommended_cpu,
                node_cpu_capacity=node_info[
                    "cpu_capacity"
                ],
                node_hourly_price=hourly_price
            )
        )

        monthly_cpu_savings = (
            CostAnalyzer.calculate_monthly_savings(
                current_cost=monthly_cpu_cost,
                optimized_cost=optimized_monthly_cpu_cost
            )
        )

        if monthly_cpu_savings > 0:

            cpu_cost_reason = (

                f"The deployment currently incurs "
                f"an estimated monthly CPU cost of "
                f"${monthly_cpu_cost}. "
                f"By resizing CPU allocation from "
                f"{round(requested_cpu, 2)} cores "
                f"to {recommended_cpu} cores, "
                f"the projected monthly CPU cost "
                f"reduces to "
                f"${optimized_monthly_cpu_cost}, "
                f"resulting in estimated savings "
                f"of ${monthly_cpu_savings} "
                f"per month."
            )

        elif monthly_cpu_savings < 0:

            cpu_cost_reason = (

                f"The deployment is currently "
                f"under-provisioned. Increasing CPU "
                f"allocation from "
                f"{round(requested_cpu, 2)} cores "
                f"to {recommended_cpu} cores "
                f"increases the estimated monthly "
                f"CPU cost from "
                f"${monthly_cpu_cost} to "
                f"${optimized_monthly_cpu_cost}. "
                f"This additional cost helps "
                f"maintain application stability."
            )

        else:

            cpu_cost_reason = (

                f"The current CPU allocation "
                f"closely matches the recommended "
                f"allocation, resulting in no "
                f"significant cost change."
            )

        # =====================
        # Memory Metrics
        # =====================

        try:

            memory_metrics = prom.get_memory_usage(
                deployment_name
            )

        except Exception:

            return {

                "error":

                "Unable to connect to Prometheus."
            }

        if not memory_metrics:

            return {

                "error":

                f"No memory metrics found "
                f"for deployment "
                f"'{deployment_name}'."
            }

        actual_memory = float(
            memory_metrics[0]["value"][1]
        )

        requested_memory = resources[
            "memory_request"
        ]

        if isinstance(requested_memory, str):

            if requested_memory.endswith("Mi"):

                requested_memory = float(
                    requested_memory.replace(
                        "Mi",
                        ""
                    )
                )

        requested_memory *= resources[
            "replicas"
        ]

        memory_waste = Analyzer.calculate_memory_waste(
            requested_memory,
            actual_memory
        )

        recommended_memory = Analyzer.recommend_memory(
            requested_memory,
            actual_memory
        )

        memory_reason = (

            f"Observed memory usage was "
            f"{round(actual_memory, 2)} MiB "
            f"against a requested allocation of "
            f"{round(requested_memory, 2)} MiB. "
            f"The recommendation enforces a "
            f"minimum allocation of "
            f"{Analyzer.MIN_MEMORY_MIB} MiB."
        )

        return {

            "deployment": deployment_name,

            "requested_cpu": round(
                requested_cpu,
                2
            ),

            "actual_cpu": round(
                actual_cpu,
                2
            ),

            "cpu_waste_percent": cpu_waste,

            "recommended_cpu": recommended_cpu,

            "cpu_recommendation_reason":
                cpu_reason,

            # CPU Cost Optimization

            "instance_type":
                instance_type,

            "node_hourly_price_usd":
                hourly_price,

            "monthly_cpu_cost_usd":
                monthly_cpu_cost,

            "optimized_monthly_cpu_cost_usd":
                optimized_monthly_cpu_cost,

            "monthly_cpu_savings_usd":
                monthly_cpu_savings,

            "cpu_cost_recommendation_reason":
                cpu_cost_reason,

            # Memory Recommendations

            "requested_memory_mib": round(
                requested_memory,
                2
            ),

            "actual_memory_mib": round(
                actual_memory,
                2
            ),

            "memory_waste_percent":
                memory_waste,

            "recommended_memory_mib":
                recommended_memory,

            "memory_recommendation_reason":
                memory_reason
        }