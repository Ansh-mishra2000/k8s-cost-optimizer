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

        print("PODS FOUND =", len(pods.items))

        running_pod = None

        print("***** NEW RUNNING POD LOGIC *****")

        for pod in pods.items:

            print(
                "POD:",
                pod.metadata.name,
                "| STATUS:",
                pod.status.phase,
                "| NODE:",
                pod.spec.node_name
            )

            if (
                pod.status.phase == "Running"
                and pod.spec.node_name is not None
            ):

                running_pod = pod

                break

        if running_pod is None:

            raise Exception(
                f"No running pod found for deployment "
                f"'{deployment_name}'."
            )

        pod_name = running_pod.metadata.name

        node_name = running_pod.spec.node_name

        print("SELECTED POD =", pod_name)

        print("NODE NAME =", node_name)

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

        deployment_list = []

        for deployment in deployments.items:

            deployment_list.append(
                {
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace
                }
            )

        return deployment_list