from kubernetes import config, client


class KubernetesService:

    def __init__(self):

        config.load_kube_config()

        self.apps_v1 = client.AppsV1Api()

    def get_deployment_resources(
        self,
        deployment_name,
        namespace="default"
    ):

        deployment = self.apps_v1.read_namespaced_deployment(
            name=deployment_name,
            namespace=namespace
        )

        container = deployment.spec.template.spec.containers[0]

        replicas = deployment.spec.replicas

        return {

            "cpu_request":
                container.resources.requests.get(
                    "cpu"
                ),

            "memory_request":
                container.resources.requests.get(
                    "memory"
                ),

            "replicas":
                replicas
        }