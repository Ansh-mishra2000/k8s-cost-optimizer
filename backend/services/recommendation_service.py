from services.kubernetes_service import KubernetesService
from services.prometheus_service import PrometheusService
from services.analyzer import Analyzer


class RecommendationService:

    def get_recommendation(self):

        k8s = KubernetesService()
        prom = PrometheusService()

        resources = k8s.get_deployment_resources(
            "stress-app"
        )

        # =====================
        # CPU Metrics
        # =====================

        cpu_metrics = prom.get_cpu_usage()

        actual_cpu = 0

        if cpu_metrics:

            for metric in cpu_metrics:

                actual_cpu += float(
                    metric["value"][1]
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

        cpu_waste = Analyzer.calculate_cpu_waste(
            requested_cpu,
            actual_cpu
        )

        recommended_cpu = Analyzer.recommend_cpu(
            requested_cpu,
            actual_cpu
        )

        # =====================
        # Memory Metrics
        # =====================

        memory_metrics = prom.get_memory_usage()

        actual_memory = 0

        if memory_metrics:

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

        memory_waste = Analyzer.calculate_memory_waste(
            requested_memory,
            actual_memory
        )

        recommended_memory = Analyzer.recommend_memory(
            requested_memory,
            actual_memory
        )

        return {

            "deployment": "stress-app",

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

            # Memory Recommendations

            "requested_memory_mib": round(
                requested_memory,
                2
            ),

            "actual_memory_mib": round(
                actual_memory,
                2
            ),

            "memory_waste_percent": memory_waste,

            "recommended_memory_mib": recommended_memory
        }