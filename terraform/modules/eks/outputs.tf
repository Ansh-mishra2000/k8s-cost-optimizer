output "cluster_name" {
  description = "The name of the EKS cluster"
  value       = aws_eks_cluster.main.name
}

output "cluster_id" {
  description = "The ID of the EKS cluster"
  value       = aws_eks_cluster.main.id
}

output "cluster_endpoint" {
  description = "The endpoint of the EKS cluster"
  value       = aws_eks_cluster.main.endpoint
}

output "cluster_certificate_authority_data" {
  description = "The base64 encoded certificate data required to communicate with the cluster"
  value       = aws_eks_cluster.main.certificate_authority[0].data
}

output "oidc_provider_arn" {
  description = "ARN of the EKS OIDC Provider"
  value       = aws_iam_openid_connect_provider.eks.arn
}

output "oidc_issuer_url" {
  description = "The OIDC Issuer URL without https://"
  value       = replace(aws_eks_cluster.main.identity[0].oidc[0].issuer, "https://", "")
}

output "node_security_group_id" {
  description = "Security group ID attached to the EKS cluster and worker nodes"
  value       = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
}

output "cluster_security_group_id" {
  description = "Primary cluster security group ID"
  value       = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
}
