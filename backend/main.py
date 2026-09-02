"""
================================================================================
 Kubernetes Cloud Cost Optimizer & FinOps AI Engine - Main Application
================================================================================
 Author: Ansh Mishra
 Description:
   FastAPI microservice that reconciles Kubernetes workload allocations against 
   live Prometheus metrics and AWS Pricing to generate AI cost-optimization 
   recommendations and historical analytics.
================================================================================
"""

import os
from fastapi import FastAPI, Query, Path, Response
from fastapi.responses import HTMLResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Database Initialization
from database.db import engine
from database.models import Base

# Core FinOps & Infrastructure Services
from services.ai_service import AIService
from services.kubernetes_service import KubernetesService
from services.prometheus_service import PrometheusService
from services.recommendation_service import RecommendationService
from services.dashboard_service import DashboardService
from services.metrics_service import MetricsService

# Initialize FastAPI App with Swagger metadata
app = FastAPI(
    title="Kubernetes Cost Optimizer & FinOps API",
    description="Automated Kubernetes right-sizing, AWS pricing analytics, and FinOps AI recommendations.",
    version="1.0.0"
)

# Auto-create database tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

# ------------------------------------------------------------------------------
# Singleton Service Instances (Initialized on Startup)
# ------------------------------------------------------------------------------
kubernetes_service = KubernetesService()
prometheus_service = PrometheusService()
recommendation_service = RecommendationService()
dashboard_service = DashboardService()
ai_service = AIService()


# ==============================================================================
# 1. ⚙️ SYSTEM & HEALTH ENDPOINTS
# ==============================================================================

@app.get("/", response_class=HTMLResponse, tags=["1. System & Health"])
@app.get("/ui", response_class=HTMLResponse, tags=["1. System & Health"])
@app.get("/dashboard", response_class=HTMLResponse, tags=["1. System & Health"])
def home():
    """Renders the modern, interactive FinOps Graphical Web Dashboard."""
    template_path = os.path.join(os.path.dirname(__file__), "templates", "dashboard.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(
        content="""
        <html>
            <body style='background:#0f172a;color:#fff;font-family:sans-serif;text-align:center;padding-top:50px;'>
                <h1>Kubernetes Cost Optimizer & FinOps Engine</h1>
                <p>Status: Healthy &bull; <a href='/docs' style='color:#38bdf8;'>Open Swagger Docs</a></p>
            </body>
        </html>
        """
    )



@app.get("/metrics", tags=["1. System & Health"])
def metrics():
    """
    Prometheus Exporter Endpoint.
    Exposes internal gauges (e.g. k8s_monthly_savings, k8s_monthly_cost) 
    for Prometheus scraping.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )



# ==============================================================================
# 2. 🧠 FINOPS AI RECOMMENDATION ENGINE (Core Optimization APIs)
# ==============================================================================

@app.get(
    "/recommendation/{namespace}/{deployment_name}",
    tags=["2. FinOps AI Recommendations"],
    summary="⭐ Core FinOps AI Recommendation Engine (Live Calculation)"
)
def get_live_recommendation(
    namespace: str = Path(..., description="Kubernetes namespace where the workload is running"),
    deployment_name: str = Path(..., description="Name of the Kubernetes Deployment to analyze")
):
    """
    ⭐ USES FINOPS AI MODEL:
    1. Reads live 5-minute CPU/RAM rates and 24-hour peak metrics from Prometheus.
    2. Fetches EC2 instance hourly pricing from AWS Pricing (cached in-memory).
    3. Runs the Smart FinOps AI Engine to generate:
       - Status: 'Severely Overprovisioned' vs 'Underprovisioned'
       - Risk Assessment with 24-hour peak safety buffer calculations
       - Exact projected monthly and annual dollar savings
       - Copy-paste ready right-sized Kubernetes manifest YAML.
    (Note: Read-only endpoint; does NOT save to the database).
    """
    result = recommendation_service.get_recommendation(
        deployment_name=deployment_name,
        namespace=namespace,
        save_to_db=False
    )

    if result is None:
        return {"error": "Recommendation service returned empty response."}

    if "error" not in result:
        # Update Prometheus metrics gauges for real-time monitoring
        MetricsService.update_metrics(result)

    return result


@app.post(
    "/collect/{namespace}/{deployment_name}",
    tags=["2. FinOps AI Recommendations"],
    summary="CronJob Ingestion Endpoint (Saves to RDS PostgreSQL)"
)
def collect_and_save_recommendation(
    namespace: str = Path(..., description="Kubernetes namespace"),
    deployment_name: str = Path(..., description="Deployment name")
):
    """
    Executed periodically by the Kubernetes CronJob (recommendation-collector).
    Runs the full FinOps calculation and PERSISTS the record into AWS RDS PostgreSQL
    for historical trending and dashboard analytics.
    """
    return recommendation_service.get_recommendation(
        deployment_name=deployment_name,
        namespace=namespace,
        save_to_db=True
    )


@app.post(
    "/recommendation/apply/{namespace}/{deployment_name}",
    tags=["2. FinOps AI Recommendations"],
    summary="⚡ Auto-Remediation Endpoint (1-Click Live Kubernetes Patch)"
)
def apply_rightsizing_remediation(
    namespace: str = Path(..., description="Kubernetes namespace"),
    deployment_name: str = Path(..., description="Deployment name to right-size")
):
    """
    ⚡ AUTO-REMEDIATION / SELF-HEALING ACTION:
    1. Runs real-time right-sizing calculation against live Prometheus & AWS Pricing.
    2. Directly PATCHES the live Kubernetes deployment container requests & limits.
    3. Triggers a Zero-Downtime rolling update across worker nodes.
    4. Logs the remediation event and projected monthly dollar savings to PostgreSQL.
    """
    return recommendation_service.apply_recommendation(
        deployment_name=deployment_name,
        namespace=namespace
    )



# ==============================================================================
# 3. 📊 POSTGRESQL DASHBOARD & SUMMARY ANALYTICS
# ==============================================================================

@app.get(
    "/dashboard/summary",
    tags=["3. Analytics & Dashboard"],
    summary="⭐ Cluster-Wide High-Level Summary API"
)
def get_dashboard_summary():
    """
    ⭐ GIVES THE SUMMARY:
    Aggregates all latest recommendations across the entire Kubernetes cluster:
    - total_deployments: Total number of analyzed workloads
    - total_monthly_cost: Total current monthly infrastructure spend in USD
    - total_monthly_savings: Total potential monthly dollar savings if right-sized
    - highest_cpu_deployment: Workload consuming the most CPU cores
    - highest_memory_deployment: Workload consuming the most RAM
    - largest_saving_deployment: Workload offering the single biggest cost-reduction opportunity.
    """
    return dashboard_service.get_dashboard_summary()


@app.get("/dashboard/top-savings", tags=["3. Analytics & Dashboard"])
def get_top_savings():
    """Returns the top 5 workloads offering the largest monthly cost reduction."""
    return dashboard_service.get_top_savings()


@app.get("/dashboard/top-cost", tags=["3. Analytics & Dashboard"])
def get_top_cost():
    """Returns the top 5 most expensive workloads running in the cluster."""
    return dashboard_service.get_top_cost()


@app.get("/dashboard/overprovisioned", tags=["3. Analytics & Dashboard"])
def get_overprovisioned_deployments():
    """Identifies workloads where allocated resources significantly exceed actual usage (Wasting Money)."""
    return dashboard_service.get_overprovisioned()


@app.get("/dashboard/underprovisioned", tags=["3. Analytics & Dashboard"])
def get_underprovisioned_deployments():
    """Identifies workloads operating near capacity (Risk of CPU throttling or OOM crashes)."""
    return dashboard_service.get_underprovisioned()


@app.get("/dashboard/utilization", tags=["3. Analytics & Dashboard"])
def get_cluster_utilization():
    """Compares total requested CPU/RAM vs actual cluster-wide consumption percentage."""
    return dashboard_service.get_cluster_utilization()


@app.get("/dashboard/history/{deployment_name}", tags=["3. Analytics & Dashboard"])
def get_deployment_history(
    deployment_name: str = Path(..., description="Deployment name to query")
):
    """Fetches all historical recommendation records for a specific deployment from PostgreSQL."""
    return dashboard_service.get_recommendation_history(deployment_name)


@app.get("/dashboard/deployment/{deployment_name}", tags=["3. Analytics & Dashboard"])
def get_latest_deployment_details(
    deployment_name: str = Path(..., description="Deployment name to query")
):
    """Fetches the latest recommendation record for a specific deployment."""
    return dashboard_service.get_deployment_details(deployment_name)


# Trend Time-Series Endpoints
@app.get("/dashboard/trends/cpu/{deployment_name}", tags=["3. Analytics & Dashboard"])
def get_cpu_trend(deployment_name: str):
    """Returns historical actual vs peak CPU trend time-series."""
    return dashboard_service.get_cpu_trend(deployment_name)


@app.get("/dashboard/trends/memory/{deployment_name}", tags=["3. Analytics & Dashboard"])
def get_memory_trend(deployment_name: str):
    """Returns historical memory consumption trend time-series."""
    return dashboard_service.get_memory_trend(deployment_name)


@app.get("/dashboard/trends/cost/{deployment_name}", tags=["3. Analytics & Dashboard"])
def get_cost_trend(deployment_name: str):
    """Returns historical current vs optimized cost trend time-series."""
    return dashboard_service.get_cost_trend(deployment_name)


@app.get("/dashboard/trends/savings/{deployment_name}", tags=["3. Analytics & Dashboard"])
def get_savings_trend(deployment_name: str):
    """Returns historical savings trend time-series."""
    return dashboard_service.get_savings_trend(deployment_name)


@app.get("/dashboard/export", tags=["3. Analytics & Dashboard"])
def export_recommendations_csv():
    """Generates and downloads a complete CSV export of all recommendation audit logs."""
    csv_data = dashboard_service.export_recommendations_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=recommendations.csv"
        }
    )


# ==============================================================================
# 4. ☸️ KUBERNETES WORKLOAD INSPECTION ENDPOINTS
# ==============================================================================

@app.get("/deployments", tags=["4. Kubernetes Inspection"])
@app.get("/dashboard/deployments", tags=["4. Kubernetes Inspection"])
def list_deployments(
    namespace: str = Query("default", description="Namespace to query (e.g. 'default' or 'optimizer')")
):
    """Lists all active deployments in a namespace, including their replica count and EC2 node instance type."""
    return kubernetes_service.get_all_deployments(namespace=namespace)


@app.get("/deployment/{deployment_name}", tags=["4. Kubernetes Inspection"])
def get_workload_specs(deployment_name: str):
    """Fetches configured CPU and Memory resource requests directly from the Kubernetes API."""
    return kubernetes_service.get_deployment_resources(deployment_name)


@app.get("/cpu/{deployment_name}", tags=["4. Kubernetes Inspection"])
def get_raw_cpu_metric(deployment_name: str):
    """Queries Prometheus directly for the live 5-minute container CPU usage vector."""
    return prometheus_service.get_cpu_usage(deployment_name)