from kubernetes import config, client


class KubernetesService:

    def __init__(self):

        config.load_kube_config()

        self.apps_v1 = client.AppsV1Api()

        self.core_v1 = client.CoreV1Api()

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

    def get_node_capacity(
        self,
        deployment_name,
        namespace="default"
    ):

        deployment = self.apps_v1.read_namespaced_deployment(
            name=deployment_name,
            namespace=namespace
        )

        labels = deployment.spec.selector.match_labels

        label_selector = ",".join(
            [
                f"{key}={value}"
                for key, value in labels.items()
            ]
        )

        pods = self.core_v1.list_namespaced_pod(
            namespace=namespace,
            label_selector=label_selector
        )

        if not pods.items:

            raise Exception(
                f"No pods found for deployment "
                f"'{deployment_name}'."
            )

        node_name = pods.items[0].spec.node_name

        node = self.core_v1.read_node(
            name=node_name
        )

        cpu_capacity = node.status.capacity[
            "cpu"
        ]

        provider_id = node.spec.provider_id

        instance_id = provider_id.split(
            "/"
        )[-1]

        return {

            "node_name":
                node_name,

            "cpu_capacity":
                float(cpu_capacity),

            "instance_id":
                instance_id
        }