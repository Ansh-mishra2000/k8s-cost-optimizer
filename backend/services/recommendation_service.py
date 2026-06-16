from services.kubernetes_service import KubernetesService
from services.prometheus_service import PrometheusService
from services.analyzer import Analyzer
from kubernetes.client.exceptions import ApiException


class RecommendationService:

    def get_recommendation(
        self,
        deployment_name
    ):

        k8s = KubernetesService()
        prom = PrometheusService()

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

        # Convert Kubernetes CPU format
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

        # Multiply by replicas
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

        # CPU Recommendation Reason
        cpu_reason = (

            f"Observed CPU usage was "
            f"{round(actual_cpu, 2)} cores "
            f"against a requested allocation of "
            f"{round(requested_cpu, 2)} cores. "
            f"The recommendation adds a 20% "
            f"safety buffer to the observed usage."
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

        # Convert Kubernetes Memory format
        if isinstance(requested_memory, str):

            if requested_memory.endswith("Mi"):

                requested_memory = float(
                    requested_memory.replace(
                        "Mi",
                        ""
                    )
                )

        # Multiply by replicas
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

        # Memory Recommendation Reason
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

            # CPU Recommendations

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