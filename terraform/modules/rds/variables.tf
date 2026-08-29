variable "project_name" {
  description = "Project name"
  type        = string
  default     = "k8s-cost-optimizer"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for DB subnet group"
  type        = list(string)
}

variable "eks_node_security_group_id" {
  description = "Security Group ID of EKS nodes to allow ingress to RDS"
  type        = string
}

variable "instance_class" {
  description = "RDS instance class (Free Tier eligible: db.t3.micro or db.t4g.micro)"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Allocated storage in GB"
  type        = number
  default     = 20
}

variable "max_allocated_storage" {
  description = "Maximum allocated storage for autoscaling in GB"
  type        = number
  default     = 100
}

variable "database_name" {
  description = "Database name"
  type        = string
  default     = "cost_optimizer_db"
}

variable "database_username" {
  description = "Database master username"
  type        = string
  default     = "optimizer_admin"
}

variable "engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "16.1"
}

variable "multi_az" {
  description = "Enable Multi-AZ deployment"
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Whether to skip final snapshot before deleting RDS"
  type        = bool
  default     = true
}
