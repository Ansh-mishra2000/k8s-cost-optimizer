from prometheus_api_client import PrometheusConnect


class PrometheusService:

    def __init__(self):

        self.prom = PrometheusConnect(
            url="http://localhost:9090",
            disable_ssl=True
        )

    def get_cpu_usage(self):

        query = '''
        rate(
            container_cpu_usage_seconds_total{
                pod=~"stress-app.*"
            }[5m]
        )
        '''

        result = self.prom.custom_query(
            query=query
        )

        return result

    def get_memory_usage(self):

        query = '''
        sum(
            container_memory_working_set_bytes{
            pod=~"stress-app.*"
            }
        ) / 1024 / 1024
        '''

        result = self.prom.custom_query(
            query=query
        )

        return result