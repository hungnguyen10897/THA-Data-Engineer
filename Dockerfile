# Image for full-stack deployment
FROM python:3.8.2

USER root

WORKDIR /app

COPY init_data/requirements.txt ./requirements.txt

# Python packages
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Terraform
RUN wget https://releases.hashicorp.com/terraform/1.0.4/terraform_1.0.4_linux_amd64.zip
RUN unzip terraform_1.0.4_linux_amd64.zip && rm terraform_1.0.4_linux_amd64.zip
RUN mv terraform /usr/bin/terraform

# This will get your .aws credentuals
COPY credentials /root/.aws/

COPY deploy.sh .

RUN chmod +x deploy.sh

CMD ["./deploy.sh"]
