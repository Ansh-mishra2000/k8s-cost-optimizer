from fastapi import FastAPI, Response

from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST
)

from database.db import engine
from database.models import Base

from services.kubernetes_service import KubernetesService
from services.prometheus_service import PrometheusService
from services.recommendation_service import RecommendationService
from services.dashboard_service import DashboardService
from services.metrics_service import MetricsService


app = FastAPI()

Base.metadata.create_all(bind=engine)


# -----------------------------
# Service Objects (Created Once)
# -----------------------------
kubernetes_service = KubernetesService()
prometheus_service = PrometheusService()
recommendation_service = RecommendationService()
dashboard_service = DashboardService()


# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():

    return {
        "message": "Kubernetes Cost Optimizer"
    }


# -----------------------------
# Deployment Resources
# -----------------------------
@app.get("/deployment/{deployment_name}")
def deployment(
    deployment_name: str
):

    return kubernetes_service.get_deployment_resources(
        deployment_name
    )


# -----------------------------
# Live CPU Usage
# -----------------------------
@app.get("/cpu/{deployment_name}")
def cpu(
    deployment_name: str
):

    return prometheus_service.get_cpu_usage(
        deployment_name
    )


# -----------------------------
# Prometheus Metrics Endpoint
# -----------------------------
@app.get("/metrics")
def metrics():

    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


# -----------------------------
# Dashboard - Deployments
# -----------------------------
@app.get("/dashboard/deployments")
def deployments():

    return kubernetes_service.get_all_deployments()


@app.get("/dashboard/deployment/{deployment_name}")
def deployment_details(
    deployment_name: str
):

    return dashboard_service.get_deployment_details(
        deployment_name
    )


# -----------------------------
# Collector Endpoint
# Used by Kubernetes CronJob
# -----------------------------
@app.post("/collect/{namespace}/{deployment_name}")
def collect(
    namespace: str,
    deployment_name: str
):

    return recommendation_service.get_recommendation(
        deployment_name,
        namespace,
        save_to_db=True
    )


# -----------------------------
# Live Recommendation
# -----------------------------
@app.get("/recommendation/{namespace}/{deployment_name}")
def recommendation_by_namespace(
    namespace: str,
    deployment_name: str
):

    result = recommendation_service.get_recommendation(
        deployment_name,
        namespace,
        save_to_db=False
    )

    if result is None:

        return {

            "error":
                "Recommendation service returned None."

        }

    if "error" not in result:

        MetricsService.update_metrics(
            result
        )

    return result


# -----------------------------
# Dashboard Summary
# -----------------------------
@app.get("/dashboard/summary")
def dashboard_summary():

    return dashboard_service.get_dashboard_summary()