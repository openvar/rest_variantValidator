
# Use an official Python runtime as a parent image
FROM python:3.6

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container's /app directory
COPY . /app

RUN apt-get update

# Updrade pip
RUN pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install -r REQUIREMENTS.txt

# Install the tool
RUN pip install -e .

# Copy the config file into the container home diorectory
COPY configuration/docker.ini /root/.variantvalidator

# Start the application with gunicorn
# CMD gunicorn -b 0.0.0.0:8000 app --workers=3 --threads=5 --worker-class=gthread --chdir ./rest_VariantValidator/
CMD gunicorn  -b 0.0.0.0:8080 app --threads=5 --worker-class=gthread --chdir ./rest_VariantValidator/
