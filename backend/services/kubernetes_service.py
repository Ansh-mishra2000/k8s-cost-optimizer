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
                f"No pods found for deployment '{deployment_name}'."
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
                f"No running pod found for deployment '{deployment_name}'."
            )

        pod_name = running_pod.metadata.name
        node_name = running_pod.spec.node_name

        print("SELECTED POD =", pod_name)
        print("NODE NAME =", node_name)

        node = self.core_v1.read_node(
            name=node_name
        )

        cpu_capacity = node.status.capacity["cpu"]

        memory_capacity = node.status.capacity["memory"]

        memory_capacity_mib = (
            int(
                memory_capacity.replace(
                    "Ki",
                    ""
                )
            ) / 1024
        )

        provider_id = node.spec.provider_id

        instance_id = provider_id.split("/")[-1]

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

            deployment_name = deployment.metadata.name

            instance_type = "Unknown"

            try:

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

                running_pod = next(
                    (
                        pod
                        for pod in pods.items
                        if (
                            pod.status.phase == "Running"
                            and pod.spec.node_name
                        )
                    ),
                    None
                )

                if running_pod:

                    node = self.core_v1.read_node(
                        name=running_pod.spec.node_name
                    )

                    instance_type = (
                        node.metadata.labels.get(
                            "node.kubernetes.io/instance-type"
                        )
                        or
                        node.metadata.labels.get(
                            "beta.kubernetes.io/instance-type"
                        )
                        or
                        "Unknown"
                    )

            except Exception as e:

                print(
                    f"Unable to determine instance type "
                    f"for {deployment_name}: {e}"
                )

            deployment_list.append(

                {

                    "name":
                        deployment_name,

                    "namespace":
                        deployment.metadata.namespace,

                    "instance_type":
                        instance_type,

                    "replicas":
                        deployment.spec.replicas or 0,

                    "ready_replicas":
                        deployment.status.ready_replicas or 0,

                    "available_replicas":
                        deployment.status.available_replicas or 0

                }

            )

        return deployment_list

    def patch_deployment_resources(
        self,
        deployment_name: str,
        namespace: str = "default",
        cpu_request: float = None,
        memory_request_mib: float = None,
        cpu_limit: float = None,
        memory_limit_mib: float = None
    ):
        """
        Dynamically patches the live Kubernetes Deployment with right-sized CPU and Memory.
        Triggers a zero-downtime rolling update.
        """
        deployment = self.apps_v1.read_namespaced_deployment(
            name=deployment_name,
            namespace=namespace
        )

        container_name = deployment.spec.template.spec.containers[0].name

        # Format CPU requests (e.g. 0.25 -> "250m", 1.0 -> "1")
        if cpu_request is not None:
            cpu_req_str = f"{int(cpu_request * 1000)}m" if cpu_request < 1.0 else f"{cpu_request}"
        else:
            cpu_req_str = "100m"

        # Format Memory requests (e.g. 64 -> "64Mi")
        if memory_request_mib is not None:
            mem_req_str = f"{int(memory_request_mib)}Mi"
        else:
            mem_req_str = "64Mi"

        # Safe default limits (2x CPU request, 1.5x Memory request)
        if cpu_limit is not None:
            cpu_lim_str = f"{int(cpu_limit * 1000)}m" if cpu_limit < 1.0 else f"{cpu_limit}"
        else:
            cpu_lim_str = f"{int(cpu_request * 2000)}m" if (cpu_request and cpu_request < 0.5) else f"{round(cpu_request * 2, 2)}"

        if memory_limit_mib is not None:
            mem_lim_str = f"{int(memory_limit_mib)}Mi"
        else:
            mem_lim_str = f"{int(memory_request_mib * 1.5)}Mi" if memory_request_mib else "128Mi"

        patch_body = {
            "spec": {
                "template": {
                    "spec": {
                        "containers": [
                            {
                                "name": container_name,
                                "resources": {
                                    "requests": {
                                        "cpu": cpu_req_str,
                                        "memory": mem_req_str
                                    },
                                    "limits": {
                                        "cpu": cpu_lim_str,
                                        "memory": mem_lim_str
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        }

        self.apps_v1.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=patch_body
        )

        return {
            "status": "success",
            "deployment": deployment_name,
            "namespace": namespace,
            "container": container_name,
            "applied_requests": {
                "cpu": cpu_req_str,
                "memory": mem_req_str
            },
            "applied_limits": {
                "cpu": cpu_lim_str,
                "memory": mem_lim_str
            }
        }