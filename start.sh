#!/bin/bash
set -e

echo "🔧 Installing system dependencies..."
apt-get update -y
apt-get install -y wget unzip curl gnupg software-properties-common jq

echo "🌐 Adding Google Chrome repository..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

echo "📦 Installing Google Chrome..."
apt-get update -y
apt-get install -y google-chrome-stable

echo "🚗 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+')
CHROME_MAJOR_VERSION=$(echo $CHROME_VERSION | cut -d. -f1)
echo "Chrome version: $CHROME_VERSION"
echo "Chrome major version: $CHROME_MAJOR_VERSION"

# For Chrome 115+, use the new Chrome for Testing API
if [ "$CHROME_MAJOR_VERSION" -ge 115 ]; then
    echo "Using Chrome for Testing API for Chrome $CHROME_MAJOR_VERSION+"
    
    # Get the latest stable ChromeDriver version for this Chrome version
    CHROMEDRIVER_URL="https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone-with-downloads.json"
    
    # Download the JSON and extract the ChromeDriver URL for Linux64
    CHROMEDRIVER_DOWNLOAD_URL=$(curl -s "$CHROMEDRIVER_URL" | jq -r ".milestones.\"$CHROME_MAJOR_VERSION\".downloads.chromedriver[] | select(.platform==\"linux64\") | .url")
    
    if [ "$CHROMEDRIVER_DOWNLOAD_URL" = "null" ] || [ -z "$CHROMEDRIVER_DOWNLOAD_URL" ]; then
        echo "❌ Could not find ChromeDriver for Chrome $CHROME_MAJOR_VERSION"
        echo "🔄 Trying alternative method..."
        
        # Fallback: try to get the latest stable version
        LATEST_STABLE=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json" | jq -r '.channels.Stable.version')
        CHROMEDRIVER_DOWNLOAD_URL="https://storage.googleapis.com/chrome-for-testing-public/$LATEST_STABLE/linux64/chromedriver-linux64.zip"
    fi
    
    echo "ChromeDriver download URL: $CHROMEDRIVER_DOWNLOAD_URL"
    
    # Download and install ChromeDriver
    wget -O /tmp/chromedriver.zip "$CHROMEDRIVER_DOWNLOAD_URL"
    unzip /tmp/chromedriver.zip -d /tmp/
    
    # Find the chromedriver binary (it might be in a subdirectory)
    CHROMEDRIVER_BINARY=$(find /tmp -name "chromedriver" -type f | head -1)
    
    if [ -z "$CHROMEDRIVER_BINARY" ]; then
        echo "❌ ChromeDriver binary not found after extraction"
        exit 1
    fi
    
    chmod +x "$CHROMEDRIVER_BINARY"
    mv "$CHROMEDRIVER_BINARY" /usr/local/bin/chromedriver
    
else
    echo "Using legacy ChromeDriver API for Chrome $CHROME_MAJOR_VERSION"
    # For older Chrome versions, use the old method
    CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_MAJOR_VERSION}")
    echo "ChromeDriver version: $CHROMEDRIVER_VERSION"
    
    wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
    unzip /tmp/chromedriver.zip -d /tmp/
    chmod +x /tmp/chromedriver
    mv /tmp/chromedriver /usr/local/bin/chromedriver
fi

echo "🧹 Cleaning up..."
rm -f /tmp/chromedriver.zip
rm -rf /tmp/chromedriver-linux64/

echo "✅ Verifying installations..."
google-chrome --version
chromedriver --version

echo "🚀 Starting Python bot..."
python3 SitResultResponse.py