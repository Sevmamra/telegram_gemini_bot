# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Run the command to start the Gunicorn server when the container launches
ENV PORT 8080
CMD ["gunicorn", "-w", "4", "--bind", "0.0.0.0:$PORT", "main:app"]
