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



@app.get("/deployment")
def deployment():

    k8s = KubernetesService()

    return k8s.get_deployment_resources(
        "payment-service"
    )

@app.get("/cpu")
def cpu():

    prom = PrometheusService()

    return prom.get_cpu_usage()

@app.get("/recommendation")
def recommendation():

    service = RecommendationService()

    return service.get_recommendation()