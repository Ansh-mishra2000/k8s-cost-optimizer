variable "project_name" {
  description = "Project name"
  type        = string
  default     = "k8s-cost-optimizer"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "cluster_version" {
  description = "Kubernetes version for EKS"
  type        = string
  default     = "1.31"
}

variable "vpc_id" {
  description = "VPC ID where EKS will be deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for EKS worker nodes"
  type        = list(string)
}

variable "public_subnet_ids" {
  description = "List of public subnet IDs for EKS"
  type        = list(string)
}

variable "ebs_csi_role_arn" {
  description = "Optional IAM Role ARN for EBS CSI Driver Addon"
  type        = string
  default     = ""
}

variable "ami_type" {
  description = "Type of Amazon Machine Image (AMI) associated with the EKS Node Group (AL2023 is required for EKS 1.30+)"
  type        = string
  default     = "AL2023_x86_64_STANDARD"
}

variable "node_instance_types" {
  description = "Instance types for the EKS node group (Free Tier: t3.micro or t2.micro)"
  type        = list(string)
  default     = ["t3.micro"]
}

variable "node_capacity_type" {
  description = "Capacity type for node group (ON_DEMAND or SPOT)"
  type        = string
  default     = "ON_DEMAND"
}

variable "node_disk_size" {
  description = "Disk size (in GiB) for worker node root volumes (Free Tier EBS limit is 30GB total)"
  type        = number
  default     = 20
}

variable "desired_size" {
  description = "Desired number of worker nodes (Free Tier: 1 node fits 750 hrs/month)"
  type        = number
  default     = 1
}

variable "min_size" {
  description = "Minimum number of worker nodes"
  type        = number
  default     = 1
}

variable "max_size" {
  description = "Maximum number of worker nodes"
  type        = number
  default     = 2
}
