output "db_instance_id" {
  description = "The RDS instance ID"
  value       = aws_db_instance.rds.id
}

output "db_instance_endpoint" {
  description = "The connection endpoint for the RDS instance"
  value       = aws_db_instance.rds.endpoint
}

output "db_instance_address" {
  description = "The address of the RDS instance"
  value       = aws_db_instance.rds.address
}

output "db_instance_port" {
  description = "The port the database is listening on"
  value       = aws_db_instance.rds.port
}

output "db_name" {
  description = "The database name"
  value       = var.database_name
}

output "db_secret_arn" {
  description = "Secrets Manager secret ARN containing credentials and DATABASE_URL"
  value       = aws_secretsmanager_secret.db_secret.arn
}

output "db_secret_name" {
  description = "Secrets Manager secret name"
  value       = aws_secretsmanager_secret.db_secret.name
}
