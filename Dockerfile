FROM python:3.9-slim

# Avoid interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies + Chrome
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && mkdir -p /etc/apt/keyrings \
    && wget -q -O /etc/apt/keyrings/google-linux-signing-key.gpg https://dl.google.com/linux/linux_signing_key.pub \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-linux-signing-key.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y --no-install-recommends google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver (auto-matched to Chrome version)
RUN set -eux; \
    CHROME_VERSION=$(google-chrome --version | grep -oE '[0-9]+' | head -1); \
    echo "Detected Chrome major version: ${CHROME_VERSION}"; \
    CHROMEDRIVER_VERSION=$(curl -sSL "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}") || true; \
    if [ -z "$CHROMEDRIVER_VERSION" ]; then \
        echo "Falling back to latest ChromeDriver version..."; \
        CHROMEDRIVER_VERSION=$(curl -sSL https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE); \
    fi; \
    echo "Installing ChromeDriver ${CHROMEDRIVER_VERSION}"; \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip"; \
    unzip chromedriver-linux64.zip -d /usr/local/bin/; \
    mv /usr/local/bin/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    chmod +x /usr/local/bin/chromedriver; \
    rm -rf chromedriver-linux64.zip /usr/local/bin/chromedriver-linux64

# Set display port (for headless Chrome)
ENV DISPLAY=:99

# Set working directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements-with-selenium.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Create non-root user and set permissions
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 10000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "--workers", "1", "--threads", "2", "--timeout", "120", "app:app"]
