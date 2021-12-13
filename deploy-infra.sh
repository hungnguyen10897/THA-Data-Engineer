#!/bin/bash

set -e

# Set up all infra
echo "Start deploying infrastructure with Terraform"
cd infra \
&& terraform init \
&& terraform apply -auto-approve

echo "Copying generated configs files to destinations"
cd ..
cp infra/{credentials,flask_configs.json} web
cp infra/data_setup_configs.json init_data

echo "Run Setup Data script"
cd init_data \
    && python data_setup.py
