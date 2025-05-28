# Zeo++ FastAPI with auto compilation
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

FROM python:3.12-slim-bullseye

# ---- System dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wget \
    make \
    tar \
    && rm -rf /var/lib/apt/lists/*

# ---- Environment variables ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ZEO_VERSION=0.3
ENV ZEO_FILENAME=zeo++-${ZEO_VERSION}.tar.gz
ENV ZEO_URL=http://www.zeoplusplus.org/${ZEO_FILENAME}
ENV ZEO_FOLDER=zeo++-${ZEO_VERSION}

WORKDIR /app

# ---- Install Python dependencies ----
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ---- Download and build Zeo++ ----
RUN wget ${ZEO_URL} && \
    tar -xzf ${ZEO_FILENAME} && \
    cd ${ZEO_FOLDER}/voro++/src && make && \
    cd ../.. && make && \
    mv network /usr/local/bin/network && \
    chmod +x /usr/local/bin/network && \
    rm -rf ${ZEO_FILENAME} ${ZEO_FOLDER}

# ---- Copy FastAPI app ----
COPY app ./app
COPY .env .env
COPY workspace ./workspace

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
