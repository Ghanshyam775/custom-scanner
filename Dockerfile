# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system-level dependencies
RUN apt-get update && apt-get install -y libzbar0

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port Flask will run on (Render assigns a dynamic port)
EXPOSE 5000

# Define the command to run your Flask app
CMD ["python", "app.py"]
