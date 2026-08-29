# Dynamic lookup for AWS default PostgreSQL engine version in the current region
data "aws_rds_engine_version" "postgres" {
  engine       = "postgres"
  default_only = true
}

# Generate a secure random password for PostgreSQL
resource "random_password" "db_password" {
  length  = 20
  special = false
}

# DB Subnet Group
resource "aws_db_subnet_group" "rds" {
  name        = "${var.project_name}-${var.environment}-db-subnet-group"
  description = "Subnet group for RDS PostgreSQL"
  subnet_ids  = var.private_subnet_ids

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-subnet-group"
    Environment = var.environment
  }
}

# RDS Security Group
resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Allow inbound PostgreSQL traffic from EKS worker nodes"
  vpc_id      = var.vpc_id

  ingress {
    description     = "PostgreSQL access from EKS nodes"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.eks_node_security_group_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-sg"
    Environment = var.environment
  }
}

# DB Parameter Group
resource "aws_db_parameter_group" "rds" {
  name   = "${var.project_name}-${var.environment}-pg-params"
  family = data.aws_rds_engine_version.postgres.parameter_group_family

  parameter {
    name  = "rds.force_ssl"
    value = "0"
  }

  tags = {
    Name        = "${var.project_name}-${var.environment}-pg-params"
    Environment = var.environment
  }
}

# RDS PostgreSQL Instance (Free Tier Compatible)
resource "aws_db_instance" "rds" {
  identifier                 = "${var.project_name}-${var.environment}-db"
  engine                     = "postgres"
  engine_version             = data.aws_rds_engine_version.postgres.version
  instance_class             = var.instance_class
  allocated_storage          = var.allocated_storage
  storage_type               = "gp3"
  db_name                    = var.database_name
  username                   = var.database_username
  password                   = random_password.db_password.result
  db_subnet_group_name       = aws_db_subnet_group.rds.name
  vpc_security_group_ids     = [aws_security_group.rds.id]
  parameter_group_name       = aws_db_parameter_group.rds.name
  multi_az                   = var.multi_az
  publicly_accessible        = false
  auto_minor_version_upgrade = true
  skip_final_snapshot        = var.skip_final_snapshot

  tags = {
    Name        = "${var.project_name}-${var.environment}-rds-postgres"
    Environment = var.environment
  }
}

# AWS Secrets Manager Secret for DB Credentials & Connection URL
resource "aws_secretsmanager_secret" "db_secret" {
  name                    = "${var.project_name}-${var.environment}-db-credentials"
  description             = "PostgreSQL credentials and connection string for ${var.project_name}"
  recovery_window_in_days = 0

  tags = {
    Name        = "${var.project_name}-${var.environment}-db-secret"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "db_secret_val" {
  secret_id = aws_secretsmanager_secret.db_secret.id
  secret_string = jsonencode({
    host         = aws_db_instance.rds.address
    port         = aws_db_instance.rds.port
    dbname       = var.database_name
    username     = var.database_username
    password     = random_password.db_password.result
    DATABASE_URL = "postgresql://${var.database_username}:${random_password.db_password.result}@${aws_db_instance.rds.address}:${aws_db_instance.rds.port}/${var.database_name}"
  })
}
