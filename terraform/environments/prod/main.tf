# 1. VPC Module
module "vpc" {
  source = "../../modules/vpc"

  project_name         = var.project_name
  environment          = var.environment
  vpc_cidr             = var.vpc_cidr
  public_subnet_cidrs  = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones   = var.availability_zones
  single_nat_gateway   = var.single_nat_gateway
  eks_cluster_name     = "${var.project_name}-${var.environment}-cluster"
}

# 2. ECR Module
module "ecr" {
  source = "../../modules/ecr"

  project_name          = var.project_name
  environment           = var.environment
  repository_names      = ["k8s-cost-optimizer", "recommendation-collector"]
  image_retention_count = 30
}

# 3. EKS Module
module "eks" {
  source = "../../modules/eks"

  project_name        = var.project_name
  environment         = var.environment
  cluster_version     = var.cluster_version
  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnet_ids
  private_subnet_ids  = module.vpc.private_subnet_ids
  node_instance_types = var.node_instance_types
  node_capacity_type  = var.node_capacity_type
  desired_size        = var.desired_nodes
  min_size            = var.min_nodes
  max_size            = var.max_nodes
}

# 4. IAM IRSA Module
module "iam_irsa" {
  source = "../../modules/iam_irsa"

  project_name             = var.project_name
  environment              = var.environment
  eks_oidc_provider_arn    = module.eks.oidc_provider_arn
  eks_oidc_issuer_url      = module.eks.oidc_issuer_url
  k8s_namespace            = var.k8s_namespace
  k8s_service_account_name = var.k8s_service_account_name
}

# 5. RDS PostgreSQL Module
module "rds" {
  source = "../../modules/rds"

  project_name               = var.project_name
  environment                = var.environment
  vpc_id                     = module.vpc.vpc_id
  private_subnet_ids         = module.vpc.private_subnet_ids
  eks_node_security_group_id = module.eks.node_security_group_id
  instance_class             = var.db_instance_class
  database_name              = var.db_name
  database_username          = var.db_username
  multi_az                   = true
  skip_final_snapshot        = false
}
