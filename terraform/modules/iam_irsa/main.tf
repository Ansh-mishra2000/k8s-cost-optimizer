# ----------------------------------------------------
# 1. EBS CSI Driver IRSA Role (Persistent Volumes)
# ----------------------------------------------------
resource "aws_iam_role" "ebs_csi_driver_role" {
  name = "${var.project_name}-${var.environment}-ebs-csi-driver-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.eks_oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${var.eks_oidc_issuer_url}:sub" = "system:serviceaccount:kube-system:ebs-csi-controller-sa"
            "${var.eks_oidc_issuer_url}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-ebs-csi-driver-role"
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "ebs_csi_policy" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"
  role       = aws_iam_role.ebs_csi_driver_role.name
}

# ----------------------------------------------------
# 2. Application IRSA Role for k8s-cost-optimizer-sa
# ----------------------------------------------------
resource "aws_iam_role" "backend_irsa_role" {
  name = "${var.project_name}-${var.environment}-backend-irsa-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = var.eks_oidc_provider_arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${var.eks_oidc_issuer_url}:sub" = "system:serviceaccount:${var.k8s_namespace}:${var.k8s_service_account_name}"
            "${var.eks_oidc_issuer_url}:aud" = "sts.amazonaws.com"
          }
        }
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-${var.environment}-backend-irsa-role"
    Environment = var.environment
  }
}

# Custom Policy for EC2 describe and AWS Pricing API
resource "aws_iam_policy" "cost_optimizer_policy" {
  name        = "${var.project_name}-${var.environment}-pricing-ec2-policy"
  description = "Permissions for k8s-cost-optimizer to fetch EC2 info and AWS pricing"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceTypes",
          "ec2:DescribeRegions",
          "pricing:GetProducts",
          "pricing:DescribeServices",
          "pricing:GetAttributeValues"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "backend_custom_policy_attach" {
  policy_arn = aws_iam_policy.cost_optimizer_policy.arn
  role       = aws_iam_role.backend_irsa_role.name
}
