#!/bin/bash

set -e

# Should be in-synch with SERVICE_NAME in deploy-web.sh
SERVICE_NAME=tha-service

# Delete Lightsail Service
aws lightsail delete-container-service --service-name $SERVICE_NAME

echo "Destroying resources from Terraform."
cd infra \
&& terraform init \
&& terraform destroy -auto-approve \
&& rm -rf .terraform* terraform.tfstate*

echo "Finish cleaning."