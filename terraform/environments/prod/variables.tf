variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "k8s-cost-optimizer"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.100.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDR blocks"
  type        = list(string)
  default     = ["10.100.1.0/24", "10.100.2.0/24", "10.100.3.0/24"]
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDR blocks"
  type        = list(string)
  default     = ["10.100.11.0/24", "10.100.12.0/24", "10.100.13.0/24"]
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]
}

variable "single_nat_gateway" {
  description = "Whether to use a single NAT Gateway (false for prod for high availability)"
  type        = bool
  default     = false
}

variable "cluster_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.31"
}

variable "node_instance_types" {
  description = "Worker node EC2 instance types"
  type        = list(string)
  default     = ["t3.large"]
}

variable "node_capacity_type" {
  description = "Node capacity type (ON_DEMAND or SPOT)"
  type        = string
  default     = "ON_DEMAND"
}

variable "desired_nodes" {
  description = "Desired number of worker nodes"
  type        = number
  default     = 3
}

variable "min_nodes" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 2
}

variable "max_nodes" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 10
}

variable "db_instance_class" {
  description = "RDS DB instance class"
  type        = string
  default     = "db.t4g.small"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "cost_optimizer_db"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "optimizer_admin"
}

variable "k8s_namespace" {
  description = "Kubernetes namespace for application"
  type        = string
  default     = "optimizer"
}

variable "k8s_service_account_name" {
  description = "Kubernetes service account for backend"
  type        = string
  default     = "k8s-cost-optimizer-sa"
}
