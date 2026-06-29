from fastapi import FastAPI
from fastapi import Response
from services.kubernetes_service import KubernetesService
from database.db import engine
from database.models import Base


from prometheus_client import (
    generate_latest,
    CONTENT_TYPE_LATEST
)

from services.kubernetes_service import (
    KubernetesService
)

from services.prometheus_service import (
    PrometheusService
)

from services.recommendation_service import (
    RecommendationService
)

from services.metrics_service import (
    MetricsService
)

app = FastAPI()

Base.metadata.create_all(bind=engine)


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

    result = service.get_recommendation(
        deployment_name,
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


@app.get("/metrics")
def metrics():

    return Response(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )

@app.get("/deployments")
def deployments():

    k8s = KubernetesService()

    return k8s.get_all_deployments()


@app.post("/collect/{namespace}/{deployment_name}")
def collect(
    namespace: str,
    deployment_name: str
):

    service = RecommendationService()

    return service.get_recommendation(
        deployment_name,
        namespace,
        save_to_db=True
    )


@app.get(
    "/recommendation/{namespace}/{deployment_name}"
)
def recommendation_by_namespace(
    namespace: str,
    deployment_name: str
):

    service = RecommendationService()

    result = service.get_recommendation(
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