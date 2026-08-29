#!/bin/bash
set -e

# ==============================================================================
# Kubernetes Cost Optimizer - End-to-End Application Deployment Script
# ==============================================================================

echo "======================================================================"
echo " 🚀 Deploying Kubernetes Cost Optimizer to AWS"
echo "======================================================================"

# Change to project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

REGION="ap-south-1"
DEV_TF_DIR="terraform/environments/dev"

echo ""
echo "🔍 [1/8] Reading Terraform Outputs..."

if [ ! -d "$DEV_TF_DIR" ]; then
  echo "❌ Error: $DEV_TF_DIR directory not found."
  exit 1
fi

TF_OUTPUT=$(terraform -chdir="$DEV_TF_DIR" output -json)

CLUSTER_NAME=$(echo "$TF_OUTPUT" | jq -r '.eks_cluster_name.value')
IRSA_ROLE_ARN=$(echo "$TF_OUTPUT" | jq -r '.backend_irsa_role_arn.value')
BACKEND_ECR_URL=$(echo "$TF_OUTPUT" | jq -r '.ecr_repository_urls.value["k8s-cost-optimizer"]')
COLLECTOR_ECR_URL=$(echo "$TF_OUTPUT" | jq -r '.ecr_repository_urls.value["recommendation-collector"]')
RDS_SECRET_NAME=$(echo "$TF_OUTPUT" | jq -r '.rds_secret_name.value')

if [ -z "$CLUSTER_NAME" ] || [ "$CLUSTER_NAME" == "null" ]; then
  echo "❌ Error: Could not read Terraform outputs. Ensure 'terraform apply' has run successfully."
  exit 1
fi

echo "  - EKS Cluster     : $CLUSTER_NAME"
echo "  - Backend IRSA    : $IRSA_ROLE_ARN"
echo "  - Backend ECR     : $BACKEND_ECR_URL"
echo "  - Collector ECR   : $COLLECTOR_ECR_URL"
echo "  - RDS Secret      : $RDS_SECRET_NAME"

echo ""
echo "🔑 [2/8] Updating kubeconfig & Optimizing Cluster for Free Tier..."
aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME"

# Optimize pod capacity on Free Tier micro instances
echo "  - Tuning CoreDNS and AWS VPC CNI for Free Tier pod density..."
kubectl scale deployment coredns -n kube-system --replicas=1 2>/dev/null || true
kubectl set env daemonset aws-node -n kube-system ENABLE_PREFIX_DELEGATION=true 2>/dev/null || true
kubectl set env daemonset aws-node -n kube-system WARM_PREFIX_TARGET=1 2>/dev/null || true

echo ""
echo "📦 [3/8] Creating Optimizer Namespace & RBAC..."
kubectl apply -f k8s/namespace.yaml

# Clean up any previous stuck pending pods
kubectl delete pods -n optimizer --field-selector=status.phase=Pending 2>/dev/null || true

# Apply RBAC and annotate ServiceAccount with IAM IRSA Role
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/collector-service-account.yaml

if [ -n "$IRSA_ROLE_ARN" ] && [ "$IRSA_ROLE_ARN" != "null" ]; then
  echo "  - Annotating k8s-cost-optimizer-sa with IRSA Role..."
  kubectl annotate serviceaccount -n optimizer k8s-cost-optimizer-sa \
    eks.amazonaws.com/role-arn="$IRSA_ROLE_ARN" --overwrite
fi

echo ""
echo "🔐 [4/8] Fetching Database Secret from AWS Secrets Manager..."
DATABASE_URL=$(aws secretsmanager get-secret-value \
  --region "$REGION" \
  --secret-id "$RDS_SECRET_NAME" \
  --query SecretString \
  --output text | jq -r .DATABASE_URL)

if [ -z "$DATABASE_URL" ] || [ "$DATABASE_URL" == "null" ]; then
  echo "❌ Error: Failed to fetch DATABASE_URL from Secrets Manager."
  exit 1
fi

kubectl create secret generic postgres-secret \
  --namespace optimizer \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --dry-run=client -o yaml | kubectl apply -f -

echo "  - PostgreSQL secret configured in 'optimizer' namespace."

echo ""
echo "🐳 [5/8] Authenticating Docker with Amazon ECR..."
ECR_REGISTRY=$(echo "$BACKEND_ECR_URL" | cut -d'/' -f1)

# Fix for Linux Docker "pass not initialized" error
if [ -f "$HOME/.docker/config.json" ]; then
  if grep -q '"credsStore"' "$HOME/.docker/config.json"; then
    echo "  - Adjusting ~/.docker/config.json to bypass uninitialized credsStore..."
    sed -i '/"credsStore"/d' "$HOME/.docker/config.json"
  fi
fi

# Detect working Docker context
if ! docker info > /dev/null 2>&1; then
  if docker context use desktop-linux > /dev/null 2>&1 && docker info > /dev/null 2>&1; then
    echo "  - Switched to 'desktop-linux' Docker context."
  elif docker context use default > /dev/null 2>&1 && docker info > /dev/null 2>&1; then
    echo "  - Switched to 'default' Docker context."
  else
    echo "❌ Error: Docker daemon is not running."
    echo "   👉 Please start Docker Desktop (or run 'sudo service docker start') and run this script again."
    exit 1
  fi
fi

aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "$ECR_REGISTRY"

echo ""
echo "🏗️ [6/8] Building and Pushing Docker Images..."

echo "  - Building Backend Image..."
docker build -t "$BACKEND_ECR_URL:latest" ./backend
echo "  - Pushing Backend Image to ECR..."
docker push "$BACKEND_ECR_URL:latest"

echo "  - Building Collector Image..."
docker build -t "$COLLECTOR_ECR_URL:latest" ./backend/collector
echo "  - Pushing Collector Image to ECR..."
docker push "$COLLECTOR_ECR_URL:latest"

echo ""
echo "🚀 [7/8] Deploying Application & Monitoring Manifests to EKS..."

# Deploy Prometheus in monitoring namespace
kubectl apply -f k8s/prometheus.yaml

# Apply Backend Deployment with dynamic image
cat k8s/backend-deployment.yaml | sed "s|image: .*|image: $BACKEND_ECR_URL:latest|g" | kubectl apply -f -

# Apply Backend Service
kubectl apply -f k8s/backend-service.yaml

# Apply Collector CronJob with dynamic image
cat k8s/cronjob.yaml | sed "s|image: .*|image: $COLLECTOR_ECR_URL:latest|g" | kubectl apply -f -

# Force Kubernetes to pull the new image and restart the pod
echo "  - Restarting backend pod to load new code..."
kubectl rollout restart deployment/k8s-cost-optimizer -n optimizer

echo ""
echo "⏳ [8/8] Waiting for Backend Rollout..."
if ! kubectl rollout status deployment/k8s-cost-optimizer -n optimizer --timeout=240s; then
  echo "⚠️ Rollout timed out or failed. Fetching pod diagnostics..."
  echo "--- Pod Status ---"
  kubectl get pods -n optimizer -o wide
  echo "--- Pod Logs ---"
  kubectl logs -n optimizer deployment/k8s-cost-optimizer --tail=30 || true
  echo "--- Pod Events ---"
  kubectl describe pod -n optimizer | tail -n 25 || true
  exit 1
fi

echo ""
echo "======================================================================"
echo " 🎉 Deployment Complete!"
echo "======================================================================"
echo ""
echo "Running Pods:"
kubectl get pods -n optimizer -o wide
echo ""
echo ""
echo "Services & Load Balancer:"
kubectl get svc -n optimizer

echo ""
echo "🌍 Fetching Public AWS Load Balancer URL..."
LB_HOSTNAME=""
for i in {1..12}; do
  LB_HOSTNAME=$(kubectl get svc -n optimizer k8s-cost-optimizer-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)
  if [ -n "$LB_HOSTNAME" ]; then
    break
  fi
  echo "  - Waiting for AWS Load Balancer DNS assignment... ($i/12)"
  sleep 5
done

echo ""
if [ -n "$LB_HOSTNAME" ]; then
  echo "🌐 Public AWS URL (Accessible from any browser anywhere!):"
  echo "   http://$LB_HOSTNAME:9000/docs"
  echo "   http://$LB_HOSTNAME:9000/dashboard/summary"
  echo "   http://$LB_HOSTNAME:9000/recommendation/default/payment-service"
else
  echo "💡 AWS Load Balancer is provisioning. Check status with:"
  echo "   kubectl get svc -n optimizer"
echo "======================================================================"
