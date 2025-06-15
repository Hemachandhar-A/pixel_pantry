# Use a lightweight Python image
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Install Chrome & dependencies only if using Selenium + Headless Chrome
RUN apt-get update && apt-get install -y \
    wget unzip xvfb libnss3 libx11-6 libglib2.0-0 \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy only backend code
COPY pixelpantry_backend/ .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Flask environment
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
EXPOSE 8080

# Start with Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
