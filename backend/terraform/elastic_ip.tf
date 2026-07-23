resource "aws_eip" "nat_a" {
  domain = "vpc"
  tags = {
    Name = "k8s-cost-optimizer-nat-eip-a"
  }
}

resource "aws_eip" "nat_b" {
  domain = "vpc"
  tags = {
    Name = "k8s-cost-optimizer-nat-eip-b"
  }
}