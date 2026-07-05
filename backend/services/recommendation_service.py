from services.kubernetes_service import KubernetesService
from services.prometheus_service import PrometheusService
from services.analyzer import Analyzer
from kubernetes.client.exceptions import ApiException
from services.aws_service import AWSService
from services.cost_analyzer import CostAnalyzer
from database.repository import RecommendationRepository



class RecommendationService:

    def get_recommendation(
        self,
        deployment_name,
        namespace="default",
        save_to_db=True
    ):
        try:

            k8s = KubernetesService()
            prom = PrometheusService()
            aws = AWSService()

            try:

                resources = k8s.get_deployment_resources(
                    deployment_name,
                    namespace
                )

            except ApiException as e:

                    return {

                        "error": str(e)
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

            avg_cpu_metrics = prom.get_avg_cpu_24h(
                    deployment_name
                )

            peak_cpu_metrics = prom.get_peak_cpu_24h(
                    deployment_name
                )

            avg_cpu_24h = 0

            peak_cpu_24h = 0

            if avg_cpu_metrics:

                avg_cpu_24h = round(
                    float(
                        avg_cpu_metrics[0]["value"][1]
                    ),
                    4
                )

            if peak_cpu_metrics:

                peak_cpu_24h = round(
                    float(
                        peak_cpu_metrics[0]["value"][1]
                    ),
                    4
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
                deployment_name,
                namespace
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

            recommended_memory, memory_explanation = Analyzer.recommend_memory(
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

            # =====================
            # Memory Cost Calculations
            # =====================

            monthly_memory_cost = (
                CostAnalyzer.calculate_monthly_memory_cost(
                    memory_allocation_mib=requested_memory,
                    node_memory_capacity_mib=node_info[
                        "memory_capacity_mib"
                    ],
                    node_hourly_price=hourly_price
                )
            )

            optimized_monthly_memory_cost = (
                CostAnalyzer.calculate_monthly_memory_cost(
                    memory_allocation_mib=recommended_memory,
                    node_memory_capacity_mib=node_info[
                        "memory_capacity_mib"
                    ],
                    node_hourly_price=hourly_price
                )
            )

            monthly_memory_savings = (
                CostAnalyzer.calculate_monthly_savings(
                    current_cost=monthly_memory_cost,
                    optimized_cost=optimized_monthly_memory_cost
                )
            )

            if monthly_memory_savings > 0:

                memory_cost_reason = (

                    f"The deployment currently incurs "
                    f"an estimated monthly memory cost of "
                    f"${monthly_memory_cost}. "
                    f"By resizing memory allocation from "
                    f"{round(requested_memory, 2)} MiB "
                    f"to {recommended_memory} MiB, "
                    f"the projected monthly memory cost "
                    f"reduces to "
                    f"${optimized_monthly_memory_cost}, "
                    f"resulting in estimated savings of "
                    f"${monthly_memory_savings} per month."
                )

            elif monthly_memory_savings < 0:

                memory_cost_reason = (

                    f"The deployment requires additional "
                    f"memory allocation. Increasing memory "
                    f"raises estimated monthly cost from "
                    f"${monthly_memory_cost} to "
                    f"${optimized_monthly_memory_cost}."
                )

            else:

                memory_cost_reason = (

                    f"The current memory allocation closely "
                    f"matches the recommended allocation, "
                    f"resulting in no significant cost change."
                )

            # =====================
            # Total Cost Calculations
            # =====================

            monthly_total_cost = (
                CostAnalyzer.calculate_total_monthly_cost(
                    cpu_cost=monthly_cpu_cost,
                    memory_cost=monthly_memory_cost
                )
            )

            optimized_monthly_total_cost = (
                CostAnalyzer.calculate_total_monthly_cost(
                    cpu_cost=optimized_monthly_cpu_cost,
                    memory_cost=optimized_monthly_memory_cost
                )
            )

            monthly_total_savings = (
                CostAnalyzer.calculate_monthly_savings(
                    current_cost=monthly_total_cost,
                    optimized_cost=optimized_monthly_total_cost
                )
            )

            if monthly_total_savings > 0:

                total_cost_reason = (

                    f"Applying all optimization recommendations "
                    f"reduces total estimated monthly cost "
                    f"from ${monthly_total_cost} to "
                    f"${optimized_monthly_total_cost}, "
                    f"resulting in estimated savings of "
                    f"${monthly_total_savings} per month."
                )

            elif monthly_total_savings < 0:

                total_cost_reason = (

                    f"The workload is currently resource "
                    f"constrained. Applying all recommendations "
                    f"increases estimated monthly cost from "
                    f"${monthly_total_cost} to "
                    f"${optimized_monthly_total_cost} "
                    f"to improve stability."
                )

            else:

                total_cost_reason = (

                    f"The current allocation already matches "
                    f"the optimizer recommendation, resulting "
                    f"in no significant cost change."
                )
            response = {

                "deployment": deployment_name,

                "requested_cpu": round(
                    requested_cpu,
                    2
                ),

                "actual_cpu": round(
                    actual_cpu,
                    2
                ),

                "avg_cpu_24h":
                    avg_cpu_24h,

                "peak_cpu_24h":
                    peak_cpu_24h,

                "cpu_waste_percent":
                    cpu_waste,

                "recommended_cpu":
                    recommended_cpu,

                "cpu_recommendation_reason":
                    cpu_reason,

                # Memory Cost Optimization

                "monthly_memory_cost_usd":
                    monthly_memory_cost,

                "optimized_monthly_memory_cost_usd":
                    optimized_monthly_memory_cost,

                "monthly_memory_savings_usd":
                    monthly_memory_savings,

                "memory_cost_recommendation_reason":
                    memory_cost_reason,

                # Total Cost Optimization

                "monthly_total_cost_usd":
                    monthly_total_cost,

                "optimized_monthly_total_cost_usd":
                    optimized_monthly_total_cost,

                "monthly_total_savings_usd":
                    monthly_total_savings,

                "total_cost_recommendation_reason":
                    total_cost_reason,

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

                "requested_memory_mib":
                    round(
                        requested_memory,
                        2
                    ),

                "actual_memory_mib":
                    round(
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
            if memory_explanation:

                response.update(memory_explanation)
                
            if save_to_db:
                try:
                    RecommendationRepository.save_recommendation(response)

                except Exception as e:
                    print("DATABASE SAVE FAILED:", str(e))

            return response
        
        except ApiException as e:

            return {
                "error": str(e)
                }
    