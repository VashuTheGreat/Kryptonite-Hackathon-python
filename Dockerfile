# ------------------------------
# Base Image
# ------------------------------
FROM python:3.10-slim-bullseye

# ------------------------------
# System dependencies
# ------------------------------
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ------------------------------
# Working directory
# ------------------------------
WORKDIR /app

# ------------------------------
# Python dependencies
# ------------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ------------------------------
# Copy application code
# ------------------------------
COPY index.py .
COPY settlelite_image_fire_coordinate.py .
COPY models ./models
COPY public ./public
COPY outputs ./outputs

# ------------------------------
# Environment variables
# ------------------------------
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# ------------------------------
# Expose FastAPI port
# ------------------------------
EXPOSE 8000

# ------------------------------
# Start FastAPI
# ------------------------------
CMD ["uvicorn", "index:app", "--host", "0.0.0.0", "--port", "8000"]
