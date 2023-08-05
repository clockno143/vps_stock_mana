# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file and install the dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app.py file into the container
COPY app.py app.py

# Expose the port your Flask app will be running on (default is 5000)
EXPOSE 5000

# Command to run your Flask app when the container starts
CMD ["python", "app.py"]
