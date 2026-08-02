resource "aws_security_group" "alb_sg" {
  name        = "alb-security-group"
  description = "security group of Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  /*ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Allow HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  } */
  tags = {
    Name        = "alb-security-group"
    Environment = "Development"
    Project     = "Kubernetes Cost Optimizer"
    Owner       = "Ansh"
    ManagedBy   = "Terraform"
  }
}

resource "aws_vpc_security_group_ingress_rule" "alb_http" {
  security_group_id = aws_security_group.alb_sg.id
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "alb_https" {
  security_group_id = aws_security_group.alb_sg.id
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "alb_outbound" {
  security_group_id = aws_security_group.alb_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
}



resource "aws_security_group" "ec2_sg" {
  name        = "ec2-security-group"
  description = "Security Group For EC2 Instance"
  vpc_id      = aws_vpc.main.id
  tags = {
    Name        = "ec2-security-group"
    Environment = "Development"
    Project     = "Kubernetes Cost Optimizer"
    Owner       = "Ansh"
    ManagedBy   = "Terraform"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ec2_http" {
  security_group_id            = aws_security_group.ec2_sg.id
  referenced_security_group_id = aws_security_group.alb_sg.id
  ip_protocol                  = "tcp"
  from_port                    = 80
  to_port                      = 80
  description                  = "Allow HTTP from ALB"
}

resource "aws_vpc_security_group_ingress_rule" "ec2_ssh" {

  security_group_id = aws_security_group.ec2_sg.id

  ip_protocol = "tcp"

  from_port = 22
  to_port   = 22

  cidr_ipv4 = "0.0.0.0/0"

  description = "Allow SSH"

}

resource "aws_vpc_security_group_egress_rule" "ec2_outbound" {
  security_group_id = aws_security_group.ec2_sg.id
  ip_protocol       = "-1"
  cidr_ipv4         = "0.0.0.0/0"
  description       = "Allow all outbound traffic"
}