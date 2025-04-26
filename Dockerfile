ARG IMGTAG=docker.io/library/python:3.10-slim@sha256:a03d346e897f21b4cf5cfc21663f3fc56394f07ce29c44043688e5bee786865b

# Base image: Use a slim Python 3.10 image
FROM $IMGTAG AS base

# Set working directory
WORKDIR /src

# Define environment variable for pip cache
ENV PIP_CACHE=/root/.cache/pip

# Copy and install Python dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=$PIP_CACHE \
    pip install  \
      -r requirements.txt

# Application stage
FROM base AS app

# Define application-specific environment variables
ENV LOG_LEVEL=INFO
ENV LOG_OUTPUT=stderr
ENV PORT=80
ENV UVICORN_PORT=80

# Copy source code
COPY src /src/src

# Run the application using Uvicorn with FastAPI
CMD ["uvicorn", "src.training_sessions.entrypoints.fastapi_app:app", "--host", "0.0.0.0", "--port", "80"]

# Development stage (based on app)
FROM app AS dev

# Install Git and other development tools
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install debugging tools
RUN pip install debugpy==1.7.0

# Embeddings setup
FROM $IMGTAG AS base_embeddings

# Set working directory
WORKDIR /app

# Define environment variables
ENV PIP_CACHE=/root/.cache/pip
ENV LOG_LEVEL=INFO
ENV LOG_OUTPUT=stderr

# Install Python dependencies for embeddings
COPY ./requirements-embeddings.txt ./requirements.txt
RUN --mount=type=cache,target=$PIP_CACHE \
    pip install  \
      --extra-index-url https://download.pytorch.org/whl/cpu \
      -r requirements.txt

#TODO: Sustituir cuando se añada Poetry
RUN pip install debugpy==1.7.0

# Development stage (based on app)
FROM app AS dev

# Install Git and other development tools
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*