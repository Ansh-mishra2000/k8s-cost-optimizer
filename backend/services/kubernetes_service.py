from kubernetes import config, client


class KubernetesService:

    def __init__(self):

        try:

            # Running locally
            config.load_kube_config()

            print(
                "Loaded local kubeconfig"
            )

        except Exception:

            # Running inside Kubernetes
            config.load_incluster_config()

            print(
                "Loaded in-cluster config"
            )

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

        memory_capacity = node.status.capacity[
            "memory"
        ]

        memory_capacity_mib = (
            int(
                memory_capacity.replace(
                    "Ki",
                    ""
                )
            ) / 1024
        )

        provider_id = node.spec.provider_id

        instance_id = provider_id.split(
            "/"
        )[-1]

        return {

            "node_name":
                node_name,

            "cpu_capacity":
                float(cpu_capacity),

            "memory_capacity_mib":
                round(
                    memory_capacity_mib,
                    2
                ),

            "instance_id":
                instance_id
        }
    def get_all_deployments(
        self,
        namespace="default"
        ):

        deployments = self.apps_v1.list_namespaced_deployment(
        namespace=namespace
        )

        deployment_names = []

        for deployment in deployments.items:

            deployment_names.append(
                deployment.metadata.name
            )

        return deployment_names