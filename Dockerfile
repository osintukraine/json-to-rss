# Use the official Python base image
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Specify the command to run your Python application
CMD ["python", "ukraine.py"]
