resource "aws_s3_bucket" "default" {
  bucket = "${var.prefix}bucket"
  acl    = "private"

  tags = var.default_tags
}

resource "aws_s3_bucket_policy" "default" {
  bucket = aws_s3_bucket.default.id

  # Terraform's "jsonencode" function converts a
  # Terraform expression's result to valid JSON syntax.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Allow public access to banner_images folder
      {
        Effect    = "Allow",
        Principal = "*",
        Action    = "s3:GetObject",
        Resource  = "${aws_s3_bucket.default.arn}/banner_images/*"
      },
      # Allow Lightsail-attached user full access to bucket
      {
        Effect = "Allow",
        Principal = {
          AWS = "${aws_iam_user.lightsail.arn}"
        },
        Action = "s3:*",
        Resource = [
          "${aws_s3_bucket.default.arn}",
          "${aws_s3_bucket.default.arn}/*"
        ]
      }
    ]
  })
}
