aws_region           = "ap-south-1"
project_name         = "k8s-cost-optimizer"
environment          = "prod"
vpc_cidr             = "10.100.0.0/16"
public_subnet_cidrs  = ["10.100.1.0/24", "10.100.2.0/24", "10.100.3.0/24"]
private_subnet_cidrs = ["10.100.11.0/24", "10.100.12.0/24", "10.100.13.0/24"]
availability_zones   = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]

single_nat_gateway  = false
cluster_version     = "1.31"
node_instance_types = ["t3.large"]
node_capacity_type  = "ON_DEMAND"
desired_nodes       = 3
min_nodes           = 2
max_nodes           = 10

db_instance_class = "db.t4g.small"
db_name           = "cost_optimizer_db"
db_username       = "optimizer_admin"

k8s_namespace            = "optimizer"
k8s_service_account_name = "k8s-cost-optimizer-sa"
