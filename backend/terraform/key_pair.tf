resource "aws_key_pair" "main" {
  key_name   = "k8s-key"
  public_key = file("C:/Users/anshm/.ssh/k8s-key.pub")
}