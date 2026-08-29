S# Terraform Cloud Infrastructure for Kubernetes Cost Optimizer

This directory contains modular Terraform configuration to provision production-ready, secure, and cost-optimized AWS infrastructure for the **Kubernetes Cost Optimizer** project.

---

## 📁 Directory Structure

```text
terraform/
├── environments/
│   ├── dev/                    # Development environment configuration
│   │   ├── main.tf             # Module orchestrator
│   │   ├── variables.tf        # Environment variable definitions
│   │   ├── terraform.tfvars    # Dev values (cost-effective sizing)
│   │   ├── outputs.tf          # Important endpoints & credentials
│   │   └── providers.tf        # AWS, Random, TLS providers
│   └── prod/                   # Production environment configuration
│       ├── main.tf             # Module orchestrator
│       ├── variables.tf        # Environment variable definitions
│       ├── terraform.tfvars    # Prod values (multi-AZ, HA sizing)
│       ├── outputs.tf          # Important endpoints & credentials
│       └── providers.tf        # AWS, Random, TLS providers
└── modules/
    ├── vpc/                    # VPC, Public/Private subnets across 3 AZs, IGW, NAT GW, Routes
    ├── eks/                    # EKS Cluster, Managed Node Group, OIDC Provider, Add-ons
    ├── rds/                    # PostgreSQL RDS Instance, Subnet Group, Secrets Manager
    ├── ecr/                    # Container Repositories with lifecycle expiration policies
    └── iam_irsa/               # IAM Roles for Service Accounts (Pricing & EC2 describe permissions)
```

---

## 🚀 Quick Start Guide

### Prerequisites
- [Terraform](https://developer.hashicorp.com/terraform/downloads) `>= 1.5.0`
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate IAM credentials (`aws configure`)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

---

### Step 1: Deploy Development Infrastructure

Navigate to the `dev` environment directory:
```bash
cd terraform/environments/dev
```

Initialize Terraform plugins:
```bash
terraform init
```

Review the planned resources:
```bash
terraform plan
```

Apply the changes to AWS:
```bash
terraform apply
```

---

### Step 2: Configure `kubectl` for the EKS Cluster

Run the command from the Terraform output:
```bash
aws eks update-kubeconfig --region ap-south-1 --name k8s-cost-optimizer-dev-cluster
```

Verify connection:
```bash
kubectl get nodes
```

---

### Step 3: Build & Push Images to Amazon ECR

1. Authenticate Docker with Amazon ECR:
```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin <YOUR_ACCOUNT_ID>.dkr.ecr.ap-south-1.amazonaws.com
```

2. Build and push backend image:
```bash
cd backend
docker build -t k8s-cost-optimizer-backend .
docker tag k8s-cost-optimizer-backend:latest <ECR_BACKEND_URL>:latest
docker push <ECR_BACKEND_URL>:latest
```

3. Build and push collector image:
```bash
cd backend/collector
docker build -t recommendation-collector .
docker tag recommendation-collector:latest <ECR_COLLECTOR_URL>:latest
docker push <ECR_COLLECTOR_URL>:latest
```

---

### Step 4: Configure Kubernetes Service Account & Database Secret

1. **Annotate Service Account with IRSA Role**:
Update `k8s/rbac.yaml` (or annotate live) with the `backend_irsa_role_arn` from Terraform output:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: k8s-cost-optimizer-sa
  namespace: optimizer
  annotations:
    eks.amazonaws.com/role-arn: <BACKEND_IRSA_ROLE_ARN_FROM_TERRAFORM_OUTPUT>
```

2. **Create Database Secret**:
Fetch the generated database URL from AWS Secrets Manager and apply it into the `optimizer` namespace:
```bash
# Retrieve DATABASE_URL from Secrets Manager
DB_URL=$(aws secretsmanager get-secret-value \
  --region ap-south-1 \
  --secret-id k8s-cost-optimizer-dev-db-credentials \
  --query SecretString \
  --output text | jq -r .DATABASE_URL)

# Create Kubernetes Secret
kubectl create namespace optimizer --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic postgres-secret \
  --namespace optimizer \
  --from-literal=DATABASE_URL="$DB_URL" \
  --dry-run=client -o yaml | kubectl apply -f -
```

3. **Deploy Kubernetes Workloads**:
```bash
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/collector-service-account.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/cronjob.yaml
```

---

## 🧹 Destroying Resources

To tear down all provisioned resources and prevent ongoing AWS charges:
```bash
cd terraform/environments/dev
terraform destroy
```
