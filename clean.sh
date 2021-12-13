#!/bin/bash

set -e

SERVICE_NAME=tha-service

# Delete Lightsail Service
aws lightsail delete-container-service --service-name $SERVICE_NAME

echo "Destroying resources from Terraform."
cd infra \
&& terraform init \
&& terraform destroy -auto-approve

echo "Finish cleaning."