variable "project_name" {
  description = "Project name"
  type        = string
  default     = "k8s-cost-optimizer"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "eks_oidc_provider_arn" {
  description = "ARN of the EKS OIDC Provider"
  type        = string
}

variable "eks_oidc_issuer_url" {
  description = "OIDC Issuer URL of the EKS Cluster without https://"
  type        = string
}

variable "k8s_namespace" {
  description = "Kubernetes namespace for the application service account"
  type        = string
  default     = "optimizer"
}

variable "k8s_service_account_name" {
  description = "Kubernetes service account name for the backend pod"
  type        = string
  default     = "k8s-cost-optimizer-sa"
}
