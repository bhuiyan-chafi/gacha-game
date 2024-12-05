# Use an official Python runtime as a parent image
FROM python:3.9.20-slim

# Install necessary system dependencies, including OpenSSL
RUN apt-get update && \
    apt-get install -y curl iputils-ping openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the entire Django project into the container
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Ensure proper permissions for SSL certificates
RUN chmod -R 600 /app/certs/*

# Expose port 8000 for Django
EXPOSE 8000

# Use the entrypoint script to manage startup
ENTRYPOINT ["sh", "-c", "python manage.py runserver_plus --cert-file certs/cert.pem --key-file certs/key.pem 0.0.0.0:8000"]