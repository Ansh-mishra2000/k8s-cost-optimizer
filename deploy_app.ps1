# ==============================================================================
# Kubernetes Cost Optimizer - PowerShell Deployment Script
# ==============================================================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " 🚀 Deploying Kubernetes Cost Optimizer to AWS" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$Region = "ap-south-1"
$DevTfDir = "terraform/environments/dev"

Write-Host "`n🔍 [1/8] Reading Terraform Outputs..." -ForegroundColor Yellow

$TfOutputJson = terraform -chdir="$DevTfDir" output -json | ConvertFrom-Json

$ClusterName = $TfOutputJson.eks_cluster_name.value
$IrsaRoleArn = $TfOutputJson.backend_irsa_role_arn.value
$BackendEcrUrl = $TfOutputJson.ecr_repository_urls.value.'k8s-cost-optimizer'
$CollectorEcrUrl = $TfOutputJson.ecr_repository_urls.value.'recommendation-collector'
$RdsSecretName = $TfOutputJson.rds_secret_name.value

Write-Host "  - EKS Cluster     : $ClusterName"
Write-Host "  - Backend IRSA    : $IrsaRoleArn"
Write-Host "  - Backend ECR     : $BackendEcrUrl"
Write-Host "  - Collector ECR   : $CollectorEcrUrl"
Write-Host "  - RDS Secret      : $RdsSecretName"

Write-Host "`n🔑 [2/8] Updating kubeconfig & Optimizing Cluster for Free Tier..." -ForegroundColor Yellow
aws eks update-kubeconfig --region $Region --name $ClusterName

kubectl scale deployment coredns -n kube-system --replicas=1
kubectl set env daemonset aws-node -n kube-system ENABLE_PREFIX_DELEGATION=true
kubectl set env daemonset aws-node -n kube-system WARM_PREFIX_TARGET=1

Write-Host "`n📦 [3/8] Creating Optimizer Namespace & RBAC..." -ForegroundColor Yellow
kubectl apply -f k8s/namespace.yaml
kubectl delete pods -n optimizer --field-selector=status.phase=Pending 2>$null
kubectl apply -f k8s/rbac.yaml
kubectl apply -f k8s/collector-service-account.yaml

if ($IrsaRoleArn) {
    Write-Host "  - Annotating k8s-cost-optimizer-sa with IRSA Role..."
    kubectl annotate serviceaccount -n optimizer k8s-cost-optimizer-sa eks.amazonaws.com/role-arn="$IrsaRoleArn" --overwrite
}

Write-Host "`n🔐 [4/8] Fetching Database Secret from AWS Secrets Manager..." -ForegroundColor Yellow
$SecretJson = aws secretsmanager get-secret-value --region $Region --secret-id $RdsSecretName --query SecretString --output text | ConvertFrom-Json
$DatabaseUrl = $SecretJson.DATABASE_URL

kubectl create secret generic postgres-secret `
    --namespace optimizer `
    --from-literal=DATABASE_URL="$DatabaseUrl" `
    --dry-run=client -o yaml | kubectl apply -f -

Write-Host "`n🐳 [5/8] Authenticating Docker with Amazon ECR..." -ForegroundColor Yellow
$EcrRegistry = $BackendEcrUrl.Split('/')[0]
aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $EcrRegistry

Write-Host "`n🏗️ [6/8] Building and Pushing Docker Images..." -ForegroundColor Yellow

Write-Host "  - Building & Pushing Backend Image..."
docker build -t "$BackendEcrUrl`:latest" ./backend
docker push "$BackendEcrUrl`:latest"

Write-Host "  - Building & Pushing Collector Image..."
docker build -t "$CollectorEcrUrl`:latest" ./backend/collector
docker push "$CollectorEcrUrl`:latest"

Write-Host "`n🚀 [7/8] Deploying Application & Monitoring Manifests to EKS..." -ForegroundColor Yellow
kubectl apply -f k8s/prometheus.yaml
(Get-Content k8s/backend-deployment.yaml) -replace "image: .*", "image: $BackendEcrUrl`:latest" | kubectl apply -f -
kubectl apply -f k8s/backend-service.yaml
(Get-Content k8s/cronjob.yaml) -replace "image: .*", "image: $CollectorEcrUrl`:latest" | kubectl apply -f -
kubectl rollout restart deployment/k8s-cost-optimizer -n optimizer

Write-Host "`n⏳ [8/8] Waiting for Backend Rollout..." -ForegroundColor Yellow
kubectl rollout status deployment/k8s-cost-optimizer -n optimizer --timeout=240s

Write-Host "`n======================================================================" -ForegroundColor Green
Write-Host " 🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green
Write-Host "`nRunning Pods:"
kubectl get pods -n optimizer -o wide
Write-Host "`nServices:"
kubectl get svc -n optimizer
Write-Host "`n💡 To access the Cost Optimizer Dashboard locally, run:" -ForegroundColor Cyan
Write-Host "   kubectl port-forward -n optimizer svc/k8s-cost-optimizer-service 9000:9000" -ForegroundColor Yellow
Write-Host "   Then open: http://localhost:9000/docs or http://localhost:9000/deployments" -ForegroundColor Yellow
Write-Host "======================================================================" -ForegroundColor Green
