#!/bin/bash

set -e

# Should be in-synch with SERVICE_NAME in clean.sh
SERVICE_NAME=tha-service

LIGHTSAIL_POWER=small
LIGHTSAIL_SCALE=1

# Build web image from within container
cd web
docker build . -t flask-tha-app

# Get status of Lightsail Service
# aws lightsail get-container-services --service-name $SERVICE_NAME


# Delete Lightsail Service
# aws lightsail delete-container-service --service-name $SERVICE_NAME

# Create Container Service
aws lightsail create-container-service --service-name $SERVICE_NAME --power $LIGHTSAIL_POWER --scale $LIGHTSAIL_SCALE || echo "Service $SERVICE_NAME is already active, updating the srevice."

# Push new image and get version of latest pushed image on Lighsail
lightsail_push_output=$(aws lightsail push-container-image --service-name $SERVICE_NAME --label $SERVICE_NAME-container --image flask-tha-app)
s1='Refer to this image as "'
rest=${lightsail_push_output#*$s1}
IMAGE_VERSION=${rest%\"*}

echo "Pushed Image Version $IMAGE_VERSION"

# Create containers.json from latest pushed image version from template_containers
sed -e "s/IMAGE_VERSION/$IMAGE_VERSION/g" template_containers.json > containers.json

# Start Service
created_service=$(aws lightsail create-container-service-deployment \
--service-name $SERVICE_NAME \
--containers file://containers.json \
--public-endpoint file://public-endpoint.json)

SERVICE_URL=$(echo $created_service | jq -r '.containerService' | jq -r '.url')
echo "Service URL: $SERVICE_URL"
echo "It can take some time before the service is ready"
