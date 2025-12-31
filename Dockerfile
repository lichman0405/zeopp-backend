# Zeo++ FastAPI Backend - Multi-stage Build
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13
# Updated: 2025-12-31 - Multi-stage build, security hardening, health check

# =============================================================================
# Stage 1: Build Stage - Compile Zeo++ and install dependencies
# =============================================================================
FROM python:3.12-slim-bullseye AS builder

# System dependencies for building Zeo++
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    make \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Environment variables for Zeo++ build
ENV ZEO_VERSION=0.3
ENV ZEO_FILENAME=zeo++-${ZEO_VERSION}.tar.gz
ENV ZEO_URL=http://www.zeoplusplus.org/${ZEO_FILENAME}
ENV ZEO_FOLDER=zeo++-${ZEO_VERSION}

WORKDIR /build

# Download and compile Zeo++
RUN wget ${ZEO_URL} && \
    tar -xzf ${ZEO_FILENAME} && \
    cd ${ZEO_FOLDER}/voro++/src && make && \
    cd ../.. && make

# Install Python dependencies to a virtual environment
COPY requirements.txt ./
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 2: Runtime Stage - Minimal image with only runtime dependencies
# =============================================================================
FROM python:3.12-slim-bullseye AS runtime

# Labels for container metadata
LABEL maintainer="Shibo Li" \
      version="0.3.1" \
      description="Zeo++ Analysis API - Porous material structure analysis service"

# Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    # Application settings
    APP_USER=zeopp \
    APP_GROUP=zeopp \
    APP_HOME=/app

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 ${APP_GROUP} && \
    useradd --uid 1000 --gid ${APP_GROUP} --shell /bin/bash --create-home ${APP_USER}

WORKDIR ${APP_HOME}

# Copy compiled Zeo++ binary from builder
COPY --from=builder /build/zeo++-0.3/network /usr/local/bin/network
RUN chmod +x /usr/local/bin/network

# Copy Python virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=${APP_USER}:${APP_GROUP} app ./app
COPY --chown=${APP_USER}:${APP_GROUP} .env .env

# Create workspace directory with proper permissions
RUN mkdir -p ./workspace && chown -R ${APP_USER}:${APP_GROUP} ./workspace

# Switch to non-root user
USER ${APP_USER}

# Expose application port
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Run application with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
