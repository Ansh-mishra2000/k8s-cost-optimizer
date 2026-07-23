resource "aws_nat_gateway" "nat_a" {
  allocation_id = aws_eip.nat_a.id
  subnet_id     = aws_subnet.public_a.id
  tags = {
    Name = "k8s-cost-optimizer-nat-gateway-a"
  }
  depends_on = [
    aws_internet_gateway.main
  ]
}

resource "aws_nat_gateway" "nat_b" {
  allocation_id = aws_eip.nat_b.id
  subnet_id     = aws_subnet.public_b.id
  tags = {
    Name = "k8s-cost-optimizer-nat-gateway-b"
  }
  depends_on = [
    aws_internet_gateway.main
  ]
}
