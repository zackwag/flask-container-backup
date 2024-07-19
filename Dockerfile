# Use a base image with Python
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt /app/

# Copy the startup script
COPY startup.sh /app/
RUN chmod +x /app/startup.sh

# Copy the application files
COPY . /app/

# Make port 2128 available to the world outside this container
EXPOSE 2128

# Run the startup script
CMD ["/app/startup.sh"]
