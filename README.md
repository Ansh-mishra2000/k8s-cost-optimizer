<div align="center">

# ⚡ Cloud-Native Kubernetes Cost Optimizer & FinOps AI Engine

[![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-%23326CE5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Terraform](https://img.shields.io/badge/Terraform-%235835CC.svg?style=for-the-badge&logo=terraform&logoColor=white)](https://www.terraform.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-%23009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-%23E6522C.svg?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-%232496ED.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

<p align="center">
  <b>An automated, enterprise-grade FinOps platform that continuously analyzes Kubernetes workload resource allocations against live utilization metrics and real-time AWS EC2 Pricing to eliminate cloud waste with zero-risk AI recommendations.</b>
</p>

### 🌐 Live World-Wide Demo
**🚀 [Click Here to Access the Live Application](https://bit.ly/cloud-k8s-cost-optimizer)**  
*(Interactive Swagger UI: `https://bit.ly/cloud-k8s-cost-optimizer/docs`)*

</div>

---

## 📌 Problem Statement

In modern containerized environments, **over 65% of cloud spend is wasted** on idle, over-provisioned Kubernetes resource requests (`cpu` and `memory`). Conversely, under-provisioned workloads risk CPU throttling and Out-Of-Memory (OOM) termination. 

This platform continuously reconciles **requested vs actual resource consumption**, computes real dollar waste against live AWS Pricing, and delivers actionable, right-sized Kubernetes manifest recommendations with intelligent risk buffers.

---

## 🌟 Key Features

* **🧠 Smart FinOps AI Reasoning Engine**: Generates executive summaries, risk evaluations, safety buffer calculations, and copy-paste right-sized Kubernetes YAML snippets with $<2\text{ MB}$ memory footprint and $\$0.00$ cloud overhead.
* **⚡ Sub-Millisecond AWS Pricing Cache**: 24-hour in-memory TTL caching with offline fallbacks for Mumbai (`ap-south-1`) instance types to eliminate trans-continental latency and AWS rate-limiting.
* **📊 Live Prometheus & cAdvisor Metrics**: Real-time extraction of 5-minute rates and 24-hour average/peak CPU and Memory metrics directly from worker node Kubelets.
* **⏰ Automated CronJob Batch Ingestion**: Periodic background collector that calculates optimization deltas across all cluster namespaces and persists historical records to PostgreSQL.
* **🔒 Zero-Trust AWS IAM Roles for Service Accounts (IRSA)**: Pod-level IAM authentication via OIDC Web Identity Federation without hardcoded AWS access keys.
* **🌐 Dynamic AWS Cloud-Native Load Balancing**: Kubernetes dynamically manages AWS Load Balancers across public subnets tagged with `kubernetes.io/role/elb = 1`.

---

## 🏛️ Modular Terraform Infrastructure

The complete cloud infrastructure is built using decoupled, reusable Terraform modules:

| Module | Location | AWS Resources Provisioned |
| :--- | :--- | :--- |
| **VPC** | [`terraform/modules/vpc`](terraform/modules/vpc) | VPC (10.0.0.0/16), 3 Public Subnets, 3 Private Subnets across 3 AZs, Internet Gateway, NAT Gateway, Route Tables with ELB tagging. |
| **EKS** | [`terraform/modules/eks`](terraform/modules/eks) | Amazon EKS Cluster v1.31, AL2023 Managed Node Groups on `t3.small` EC2 instances, CloudWatch Log Groups. |
| **RDS** | [`terraform/modules/rds`](terraform/modules/rds) | PostgreSQL DB (`db.t3.micro`, 20GB gp3 storage) with dynamic RDS engine lookup and AWS Secrets Manager integration. |
| **ECR** | [`terraform/modules/ecr`](terraform/modules/ecr) | Amazon Elastic Container Repositories with automated image lifecycle retention policies. |
| **IAM / IRSA** | [`terraform/modules/iam_irsa`](terraform/modules/iam_irsa) | OpenID Connect (OIDC) Identity Provider, EBS CSI Driver IRSA Role, and Custom FinOps EC2/Pricing IAM Policies. |

---

## 🛡️ Complete Policy & Security Matrix (11 Policies)

This project strictly adheres to the principle of **Least Privilege (PoLP)** across 11 policies:

```
├── AWS IAM Policies (8 Total)
│   ├── EKS Control Plane (2 Policies): AmazonEKSClusterPolicy, AmazonEKSVPCResourceController
│   ├── EKS Worker Nodes (4 Policies): AmazonEKSWorkerNodePolicy, AmazonEKS_CNI_Policy, AmazonEC2ContainerRegistryReadOnly, AmazonSSMManagedInstanceCore
│   └── Pod-Level IRSA (2 Policies): AmazonEBSCSIDriverPolicy, k8s-cost-optimizer-pricing-ec2-policy (Custom Least-Privilege Policy)
├── Kubernetes RBAC Policies (2 Total)
│   ├── k8s-cost-optimizer-role (ClusterRole for Deployments, Pods, Nodes)
│   └── prometheus-role (ClusterRole for Node/cAdvisor Metrics)
└── AWS ECR Lifecycle Policies (1 Total)
    └── Automated Image Retention Policy (Keeps last 5 builds to prevent storage charges)
```

---

## 🚀 Getting Started & Deployment Runbook

### 1. Prerequisites
* [AWS CLI](https://aws.amazon.com/cli/) configured with administrator credentials
* [Terraform v1.5+](https://www.terraform.io/downloads)
* [kubectl](https://kubernetes.io/docs/tasks/tools/) & [Docker](https://www.docker.com/)

---

### 2. Provision AWS Infrastructure via Terraform

```bash
cd terraform/environments/dev
terraform init
terraform plan
terraform apply -auto-approve
```

---

### 3. Deploy Applications & Monitoring Stack

Run the automated one-click deployment script from the project root:

```bash
./deploy_app.sh
```

---

### 4. Deploy Sample Target Workloads

```bash
kubectl apply -f k8s/payment-service.yaml
kubectl apply -f k8s/stress-deployment.yaml
```

---

## 📊 Sample FinOps AI Recommendation Output

```json
{
  "deployment": "stress-app",
  "requested_cpu": 0.1,
  "actual_cpu": 0.25,
  "avg_cpu_24h": 0.2109,
  "peak_cpu_24h": 0.25,
  "recommended_cpu": 0.3,
  "instance_type": "t3.small",
  "monthly_total_cost_usd": 5.48,
  "optimized_monthly_total_cost_usd": 12.06,
  "monthly_total_savings_usd": -6.58,
  "ai_analysis": {
    "status": "Underprovisioned (Throttling Risk)",
    "risk_level": "Very Low",
    "summary": "Deployment 'stress-app' is operating near capacity (250.0% CPU utilization). Increasing resource requests is recommended to prevent throttling under peak traffic.",
    "risk_assessment": "Low Risk: 24h peak CPU was 0.25 cores. The recommended allocation of 0.3 cores preserves a 16.7% safety buffer above observed peaks.",
    "financial_impact": "Right-sizing adds $6.58/month to ensure cluster stability and eliminate OOM kill risks.",
    "action_item": "Update 'k8s/stress-app.yaml' with requests of 300m CPU and 64Mi memory. Run 'kubectl apply -f k8s/stress-app.yaml'.",
    "recommended_yaml_snippet": "resources:\n  requests:\n    cpu: \"300m\"\n    memory: \"64Mi\"\n  limits:\n    cpu: \"600m\"\n    memory: \"96Mi\""
  }
}
```

---

## 📖 API Endpoint Reference

| Method & Route | Description | Target Component |
| :--- | :--- | :--- |
| `GET /docs` | Interactive Swagger UI API Explorer | FastAPI Core |
| `GET /recommendation/{namespace}/{name}` | Real-time FinOps analysis with AI risk assessment | FinOps AI Engine |
| `POST /collect/{namespace}/{name}` | Scheduled batch metric calculation and RDS ingestion | CronJob Collector |
| `GET /dashboard/summary` | Cluster-wide monthly spend and potential savings | PostgreSQL RDS |
| `GET /dashboard/top-savings` | Top 5 workloads offering highest cost reduction | PostgreSQL RDS |
| `GET /dashboard/overprovisioned` | Deployments wasting excessive allocated resources | PostgreSQL RDS |
| `GET /dashboard/underprovisioned` | Deployments at risk of CPU throttling or OOM | PostgreSQL RDS |
| `GET /dashboard/export` | Export full recommendation audit history to CSV | Reporting Engine |
| `GET /metrics` | Prometheus metrics scrape endpoint | Prometheus Client |

---

## 📄 Full Architecture Design Document

A complete, 4-page architecture whitepaper PDF is included in this repository:  
👉 **[`AWS_Terraform_and_Kubernetes_Architecture.pdf`](AWS_Terraform_and_Kubernetes_Architecture.pdf)**

---

## 🧹 Teardown (Prevent Cloud Charges)

To cleanly destroy all created AWS infrastructure and eliminate all costs:

```bash
# 1. Delete Kubernetes LoadBalancer (removes AWS ELB):
kubectl delete svc k8s-cost-optimizer-service -n optimizer

# 2. Delete test workloads:
kubectl delete -f k8s/payment-service.yaml -f k8s/stress-deployment.yaml

# 3. Destroy all Terraform cloud resources:
cd terraform/environments/dev
terraform destroy -auto-approve
```

---

## 👤 Author

**Ansh Mishra**
* GitHub: [@Ansh-mishra2000](https://github.com/Ansh-mishra2000)
* Project Repository: [https://github.com/Ansh-mishra2000/k8s-cost-optimizer](https://github.com/Ansh-mishra2000/k8s-cost-optimizer)
