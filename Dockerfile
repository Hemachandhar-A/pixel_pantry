# ---------- FRONTEND STAGE ----------
FROM node:18 AS frontend

# Set working directory inside the container
WORKDIR /GIT_PIX

# Copy your frontend source code into the container
# Assuming your frontend code is in a 'pixelpantry-frontend' directory relative to the Dockerfile
COPY pixelpantry-frontend/ .

# Install dependencies
RUN npm install

# Build the production-ready Vite frontend (outputs to /webapp/dist)
RUN npm run build


# ---------- BACKEND STAGE ----------
# Using python:3.11-slim-bookworm for a specific, stable Python 3.11 version on Debian Bookworm
FROM python:3.11-slim-bookworm AS backend

# Set working directory inside the container
WORKDIR /webapp

# Install system dependencies needed for Python packages and Chrome.
# 'build-essential' for compiling some Python wheels.
# 'wget', 'unzip', 'xvfb' for downloading/running ChromeDriver, and X virtual framebuffer.
# 'libnss3', 'libglib2.0-0', 'libx11-6' are common for Chrome headless.
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    unzip \
    xvfb \
    libnss3 \
    libglib2.0-0 \
    libx11-6 \
    # Add libgconf-2-4 if needed for older Chrome versions or specific dependencies
    # libgconf-2-4 \
    # libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm-dev libatspi2.0-0 \
    # libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libxtst6 libnss3 libxss1 libasound2 libgbm1 \
    # Clean up apt cache to keep image size small
    && rm -rf /var/lib/apt/lists/*

# Install Chrome (modern, recommended method for Debian/Ubuntu)
# Adds Google's GPG key and then their repository.
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    # Clean up apt cache again
    && rm -rf /var/lib/apt/lists/*

# Copy backend source code into the container
# Assuming your backend code is in a 'pixelpantry_backend' directory relative to the Dockerfile
COPY pixelpantry_backend/ .

# Install Python dependencies (requirements.txt should be inside pixelpantry_backend and now at /webapp/requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the built frontend (Vite dist folder) from frontend stage to Flask static folder
# This makes the frontend accessible from your Flask app if serving static files
COPY --from=frontend /webapp/dist/ ./static/

# Set Flask environment variables
ENV FLASK_APP=app.py
# FLASK_RUN_PORT is for Flask's dev server, Gunicorn will bind to 0.0.0.0:8080 directly
# ENV FLASK_RUN_PORT=8080 
ENV FLASK_ENV=production # Good practice for production

# Expose the port where your Gunicorn server will listen
EXPOSE 8080

# Start Flask server using Gunicorn (PRODUCTION-READY COMMAND)
# Make sure your Flask app instance is named 'app' in 'app.py' within pixelpantry_backend.
# If your app instance is different or in another file, adjust 'app:app' accordingly.
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]