# Generating files from outputs of Terraform Configurations

# To be used by web module to authenticate calls to S3 bucket
resource "local_file" "lightsail_user_credentials" {
  filename = "${path.module}/credentials"
  content  = <<EOF
[default]
aws_access_key_id = ${aws_iam_access_key.lightsail.id}
aws_secret_access_key = ${aws_iam_access_key.lightsail.secret}
  EOF
}

resource "random_password" "flask_secret_key" {
  length  = 16
  special = true
}

resource "random_password" "redshift_tha_user_password" {
  length      = 8
  special     = false
  min_numeric = 1
}


# To be used by Flask app to access database and S3 bucket
resource "local_file" "flask_configs" {
  filename = "${path.module}/flask_configs.json"
  content  = <<EOF
{
  "FLASK_SECRET_KEY": "${random_password.flask_secret_key.result}",
  "REDSHIFT_HOST": "${aws_redshift_cluster.default.endpoint}",
  "REDSHIFT_PORT": "${aws_redshift_cluster.default.port}",
  "REDSHIFT_DATABASE": "${aws_redshift_cluster.default.database_name}",
  "REDSHIFT_THA_USER": "${var.redshift_tha_user}",
  "REDSHIFT_THA_USER_PASSWORD": "${random_password.redshift_tha_user_password.result}",
  "BUCKET": "${aws_s3_bucket.default.bucket}",
  "BANNER_IMAGES_URL": "https://${aws_s3_bucket.default.bucket_domain_name}/banner_images/"
}
EOF
}

# To be used by init_data/data_setup.py script to populate initial data and set up database
resource "local_file" "data_setup_configs" {
  filename = "${path.module}/data_setup_configs.json"
  content  = <<EOF
{
  "REDSHIFT_HOST": "${aws_redshift_cluster.default.endpoint}",
  "REDSHIFT_PORT": "${aws_redshift_cluster.default.port}",
  "REDSHIFT_DATABASE": "${aws_redshift_cluster.default.database_name}",
  "REDSHIFT_MASTER_USER": "${aws_redshift_cluster.default.master_username}",
  "REDSHIFT_MASTER_PASSWORD": "${aws_redshift_cluster.default.master_password}",
  "REDSHIFT_THA_USER": "${var.redshift_tha_user}",
  "REDSHIFT_THA_USER_PASSWORD": "${random_password.redshift_tha_user_password.result}",
  "REDSHIFT_SPECTRUM_ROLE_ARN": "${aws_iam_role.redshift.arn}",
  "BUCKET": "${aws_s3_bucket.default.bucket}"
}
EOF
}
