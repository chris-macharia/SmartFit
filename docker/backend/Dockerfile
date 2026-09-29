# ============================================================
# SmartFit Backend Dockerfile
# ============================================================
#
# Python 3.12 + FastAPI + OpenCV + MediaPipe
#
# The application source is copied from the repository's
# backend/ directory into /app inside the container.
# ============================================================

FROM python:3.12-slim

# Prevent Python from creating .pyc files and ensure that
# Python output appears immediately in Docker logs.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container.
WORKDIR /app

# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------
#
# OpenCV and MediaPipe may require system libraries that are
# not included in the slim Python image.
#
# libegl1, libgles2, libgl1, libglib2.0-0, libgomp1, libsm6, libxext6 and ffmpeg provide common runtime libraries
# required by OpenCV.
# ------------------------------------------------------------

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libegl1 \
        libgles2 \
        libgl1 \
        libglib2.0-0 \
        libgomp1 \
        libsm6 \
        libxext6 \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------------------------------------
# Python dependencies
# ------------------------------------------------------------

COPY backend/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------
# SmartFit application
# ------------------------------------------------------------

COPY backend/app ./app
COPY backend/models ./models
COPY backend/scripts ./scripts

# Create the directory used by SmartFit for uploaded videos
# and generated avatar files.
RUN mkdir -p /app/uploads/videos \
    /app/uploads/avatars

# ------------------------------------------------------------
# FastAPI
# ------------------------------------------------------------

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]