from prometheus_api_client import PrometheusConnect


class PrometheusService:

    def __init__(self):

        self.prom = PrometheusConnect(
            url="http://monitoring-kube-prometheus-prometheus.monitoring:9090",
            disable_ssl=True
        )

    def get_cpu_usage(
        self,
        deployment_name
    ):

        query = f'''
        sum(
            rate(
                container_cpu_usage_seconds_total{{
                    pod=~"{deployment_name}.*",
                    image!=""
                }}[5m]
            )
        )
        '''

        result = self.prom.custom_query(
            query=query
        )

        return result

    def get_memory_usage(
        self,
        deployment_name
    ):

        query = f'''
        sum(
            container_memory_working_set_bytes{{
                pod=~"{deployment_name}.*",
                image!=""
            }}
        ) / 1024 / 1024
        '''

        result = self.prom.custom_query(
            query=query
        )

        return result