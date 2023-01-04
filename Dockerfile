
# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container's /app directory
COPY . /app

# Create logging directory
RUN mkdir /usr/local/share/logs

# Update apt-get
RUN apt-get update

# Install git
RUN apt-get -y install git

# Updrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install -r REQUIREMENTS.txt

# Install the tool
RUN pip install -e .

# Copy the config file into the container home diorectory
COPY configuration/docker.ini /root/.variantvalidator

# Start the application with gunicorn
CMD gunicorn  -b 0.0.0.0:8000 app --threads=5 --chdir ./rest_VariantValidator/