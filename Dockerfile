# Use Debian 11 (Bullseye) for maximum package compatibility
FROM python:3.10-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

# Set work directory
WORKDIR /app

# Install system dependencies (Debian 11 Stable List)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxrender1 \
    libxcursor1 \
    libxft2 \
    libxinerama1 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libgdk-pixbuf2.0-0 \
    shared-mime-info \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Build frontend (Optional: Render can do this, but safe to have structure)
# For this "Backend-First" flow, we assume frontend static files are committed in frontend/dist
# If not, we would need nodejs here. 
# We are currently committing frontend/dist, so we don't need Node in this container.

# Expose port (Render sets $PORT env var, but good practice)
EXPOSE 8000

# Grant permissions (Fixes SQLite "attempt to write a readonly database" zombie)
RUN chmod -R 777 /app

# Run the application
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
