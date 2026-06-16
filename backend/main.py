from fastapi import FastAPI
from services.kubernetes_service import KubernetesService
from services.prometheus_service import (
    PrometheusService
)
from services.recommendation_service import (
    RecommendationService
)

app = FastAPI()


@app.get("/")
def home():

    return {
        "message": "Kubernetes Cost Optimizer"
    }


@app.get("/deployment/{deployment_name}")
def deployment(
    deployment_name: str
):

    k8s = KubernetesService()

    return k8s.get_deployment_resources(
        deployment_name
    )


@app.get("/cpu/{deployment_name}")
def cpu(
    deployment_name: str
):

    prom = PrometheusService()

    return prom.get_cpu_usage(
        deployment_name
    )


@app.get("/recommendation/{deployment_name}")
def recommendation(
    deployment_name: str
):

    service = RecommendationService()

    return service.get_recommendation(
        deployment_name
    )