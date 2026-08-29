aws_region           = "ap-south-1"
project_name         = "k8s-cost-optimizer"
environment          = "dev"
vpc_cidr             = "10.0.0.0/16"
public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
availability_zones   = ["ap-south-1a", "ap-south-1b", "ap-south-1c"]

single_nat_gateway  = true
cluster_version     = "1.31"
node_instance_types = ["t3.small"]
node_capacity_type  = "ON_DEMAND"
desired_nodes       = 2
min_nodes           = 1
max_nodes           = 2

db_instance_class = "db.t3.micro"
db_name           = "cost_optimizer_db"
db_username       = "optimizer_admin"

k8s_namespace            = "optimizer"
k8s_service_account_name = "k8s-cost-optimizer-sa"
