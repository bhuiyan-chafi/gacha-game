# Use an official Python runtime as a parent image
FROM python:3.9.20-slim

# Install necessary system dependencies including curl
RUN apt-get update && \
    apt-get install -y curl iputils-ping && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the Django project into the container
COPY . /app

# Install pipenv and project dependencies
RUN pip install --upgrade pip && pip install pipenv && pipenv install --system --deploy && pip install -r requirements.txt

# Expose port 8000 to allow access to the Django app
EXPOSE 8000

# Use the entrypoint script to manage startup
ENTRYPOINT ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]