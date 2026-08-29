variable "project_name" {
  description = "Project name for repository naming"
  type        = string
  default     = "k8s-cost-optimizer"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "repository_names" {
  description = "List of ECR repository names to create"
  type        = list(string)
  default     = ["k8s-cost-optimizer", "recommendation-collector"]
}

variable "image_retention_count" {
  description = "Number of untagged/latest images to retain"
  type        = number
  default     = 10
}
