# User for Lightsail authorization
resource "aws_iam_user" "lightsail" {
  name = "${var.prefix}-lightsail-container-service"

  tags = var.default_tags
}

resource "aws_iam_access_key" "lightsail" {
  user = aws_iam_user.lightsail.name
}
