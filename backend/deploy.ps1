Write-Host ""
Write-Host "====================================="
Write-Host " Kubernetes Cost Optimizer Deployment"
Write-Host "====================================="
Write-Host ""

$image = "085351677198.dkr.ecr.ap-south-1.amazonaws.com/k8s-cost-optimizer:latest"

Write-Host "[1/6] Building Docker Image..."
docker build -t k8s-cost-optimizer .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker build failed!"
    exit
}

Write-Host ""

Write-Host "[2/6] Tagging Image..."
docker tag k8s-cost-optimizer:latest $image

Write-Host ""

Write-Host "[3/6] Pushing Image to Amazon ECR..."
docker push $image

if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker push failed!"
    exit
}

Write-Host ""

Write-Host "[4/6] Restarting Kubernetes Deployment..."
kubectl rollout restart deployment k8s-cost-optimizer -n optimizer

Write-Host ""

Write-Host "[5/6] Waiting for Rollout..."
kubectl rollout status deployment k8s-cost-optimizer -n optimizer

Write-Host ""

Write-Host "[6/6] Current Pods"
kubectl get pods -n optimizer

Write-Host ""
Write-Host "Deployment Completed Successfully!"