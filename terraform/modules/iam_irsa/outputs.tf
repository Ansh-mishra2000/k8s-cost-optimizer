output "ebs_csi_driver_role_arn" {
  description = "EBS CSI Driver IRSA Role ARN"
  value       = aws_iam_role.ebs_csi_driver_role.arn
}

output "backend_irsa_role_arn" {
  description = "Backend Cost Optimizer IRSA Role ARN"
  value       = aws_iam_role.backend_irsa_role.arn
}
