# Use the Alpine-based Python image for a minimal runtime
FROM python:alpine

# Set environment variables to prevent Python from writing .pyc files and to enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Build arguments for assigning user and group IDs (can be overridden at build-time)
ARG USER_ID=1000
ARG GROUP_ID=1000

# Create a non-root user and group using Alpine's addgroup and adduser
RUN addgroup -g ${GROUP_ID} appuser && \
    adduser -D -u ${USER_ID} -G appuser appuser

# Set the working directory
WORKDIR /app

# Copy the requirements file separately to leverage Docker cache
COPY requirements.txt /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY ./app /app

# Change ownership of the work directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to the non-root user for improved security
USER appuser

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI application using uvicorn with autoreload enabled
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]