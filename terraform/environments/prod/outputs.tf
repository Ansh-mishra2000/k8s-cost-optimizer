output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "eks_cluster_name" {
  description = "EKS Cluster Name"
  value       = module.eks.cluster_name
}

output "eks_cluster_endpoint" {
  description = "EKS API Server Endpoint"
  value       = module.eks.cluster_endpoint
}

output "ecr_repository_urls" {
  description = "ECR Image Repository URLs"
  value       = module.ecr.repository_urls
}

output "rds_endpoint" {
  description = "RDS PostgreSQL Endpoint"
  value       = module.rds.db_instance_endpoint
}

output "rds_secret_name" {
  description = "Secrets Manager secret name containing DB credentials and connection string"
  value       = module.rds.db_secret_name
}

output "backend_irsa_role_arn" {
  description = "IAM Role ARN to annotate on the Kubernetes Service Account"
  value       = module.iam_irsa.backend_irsa_role_arn
}

output "configure_kubectl_command" {
  description = "Command to configure kubectl context with the newly created EKS cluster"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}
