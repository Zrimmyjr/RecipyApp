# Set base image (host OS)
FROM python:3.10-slim

# By default, listen on port 5000
EXPOSE 80

# Set the working directory in the container
WORKDIR /Flask-Web-App-Tutorial-main

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install any dependencies
RUN pip install -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Specify the command to run on container start
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:80", "main:app"]


