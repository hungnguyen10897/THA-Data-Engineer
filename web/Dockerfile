# Set base image (host OS)
FROM python:3.8.2

# By default, listen on port 5000
EXPOSE 8080/tcp

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .
COPY credentials /root/.aws/

# COPY credentials /root/.aws/

# Install any dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY src ./src/
COPY flask_configs.json .
COPY run.py .
COPY run.sh .
RUN chmod +x run.sh

# Specify the command to run on container start
CMD [ "./run.sh" ]
