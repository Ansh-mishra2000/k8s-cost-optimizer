resource "aws_launch_template" "web_lt" {
  name_prefix = "web-launch-template-"

  image_id = data.aws_ami.ubuntu.id

  instance_type = "t3.micro"

  key_name = aws_key_pair.main.key_name

  vpc_security_group_ids = [
    aws_security_group.ec2_sg.id
  ]

  user_data = base64encode(
    file("${path.module}/user_data.sh")
  )
  tag_specifications {
    resource_type = "instance"

    tags = {
      Name        = "web-server"
      Environment = "Development"
      Project     = "Kubernetes Cost Optimizer"
      Owner       = "Ansh"
      ManagedBy   = "Terraform"
    }
  }

  tags = {
    Name = "Web-launch-template"
  }

}