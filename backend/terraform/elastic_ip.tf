resource "aws_eip" "nat" {
  domain = "vpc"
  tags = {
    Name = "k8s-cost-optimizer-nat-eip"
  }
}