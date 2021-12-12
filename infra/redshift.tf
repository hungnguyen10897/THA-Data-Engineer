# Main policy for redshift to access resources
resource "aws_iam_policy" "redshift" {
  name        = "${var.prefix}-redshift-spectrum-policy"
  description = "Policy for redshfit to access resources"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:ListMultipartUploadParts",
          "s3:ListBucket",
          "s3:ListBucketMultipartUploads"
        ],
        Resource = [
          "${aws_s3_bucket.default.arn}",
          "${aws_s3_bucket.default.arn}/*"
        ]
      },
      {
        Effect = "Allow",
        Action = [
          "glue:CreateDatabase",
          "glue:DeleteDatabase",
          "glue:GetDatabase",
          "glue:GetDatabases",
          "glue:UpdateDatabase",
          "glue:CreateTable",
          "glue:DeleteTable",
          "glue:BatchDeleteTable",
          "glue:UpdateTable",
          "glue:GetTable",
          "glue:GetTables",
          "glue:BatchCreatePartition",
          "glue:CreatePartition",
          "glue:DeletePartition",
          "glue:BatchDeletePartition",
          "glue:UpdatePartition",
          "glue:GetPartition",
          "glue:GetPartitions",
          "glue:BatchGetPartition"
        ],
        Resource = [
          "*"
        ]
      }
    ]
  })

  tags = var.default_tags
}

# Role for Redshift
resource "aws_iam_role" "redshift" {
  name = "${var.prefix}-redshift-spectrum"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = [
            "redshift.amazonaws.com"
          ]
        },
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.default_tags
}

resource "aws_iam_role_policy_attachment" "redshift" {
  role       = aws_iam_role.redshift.name
  policy_arn = aws_iam_policy.redshift.arn
}

resource "aws_redshift_cluster" "default" {
  cluster_identifier  = "${var.prefix}-redshift-cluster"
  database_name       = "tha"
  master_username     = "hung"
  master_password     = "Hung1111"
  node_type           = "dc2.large"
  cluster_type        = "single-node"
  iam_roles           = [aws_iam_role.redshift.arn]
  skip_final_snapshot = true

  tags = var.default_tags
}

# For the Redshift role to create database in Glue Data Catalog
resource "aws_lakeformation_permissions" "redshift" {
  principal        = aws_iam_role.redshift.arn
  permissions      = ["CREATE_DATABASE"]
  catalog_resource = true
}
