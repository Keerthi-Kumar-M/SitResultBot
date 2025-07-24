#!/bin/bash
set -e

echo "🔧 Installing system dependencies..."
apt-get update -y
apt-get install -y wget unzip curl gnupg software-properties-common

echo "🌐 Adding Google Chrome repository..."
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

echo "📦 Installing Google Chrome..."
apt-get update -y
apt-get install -y google-chrome-stable

echo "🚗 Installing ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
echo "Chrome version: $CHROME_VERSION"

# Get the latest ChromeDriver version that matches Chrome
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}")
echo "ChromeDriver version: $CHROMEDRIVER_VERSION"

wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"
unzip /tmp/chromedriver.zip -d /tmp/
chmod +x /tmp/chromedriver
mv /tmp/chromedriver /usr/local/bin/chromedriver

echo "🧹 Cleaning up..."
rm -f /tmp/chromedriver.zip

echo "✅ Verifying installations..."
google-chrome --version
chromedriver --version

echo "🚀 Starting Python bot..."
python3 SitResultResponse.py