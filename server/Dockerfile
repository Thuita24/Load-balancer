# Use Python base image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy server code
COPY server.py .

# Install Flask
RUN pip install flask

# Expose port
EXPOSE 5000

# Run the server
CMD ["python", "server.py"]
