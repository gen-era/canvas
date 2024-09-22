# Use the official Python image from the Docker Hub
FROM python:3.12.6-slim-bookworm

# Set environment variables to ensure that Python output is sent straight to the terminal (e.g., logs)
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .
