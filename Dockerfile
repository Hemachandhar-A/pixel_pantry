FROM python:3.11-slim-bookworm

WORKDIR /app

# Install Chrome + minimal system deps (only if needed by Selenium)
RUN apt-get update && apt-get install -y \
    wget unzip xvfb libnss3 libx11-6 libglib2.0-0 \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY pixelpantry_backend/ .

# Copy frontend build output to Flask static folder
COPY pixelpantry-frontend/dist/ ./static/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
EXPOSE 8080

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080"]
