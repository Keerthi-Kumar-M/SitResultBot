#!/bin/bash
set -e

# Install dependencies
apt-get update -y
apt-get install -y wget unzip curl gnupg

# Use known compatible version
CHROME_VERSION="118.0.5993.117"

echo "✅ Installing Chrome version $CHROME_VERSION"

# Download and install Chrome
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chrome-linux64.zip -O chrome.zip
unzip chrome.zip
mv chrome-linux64 /opt/chrome
ln -s /opt/chrome/chrome /usr/bin/google-chrome

# Download Chromedriver
wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chromedriver-linux64.zip -O chromedriver.zip
unzip chromedriver.zip
chmod +x chromedriver-linux64/chromedriver
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# Cleanup
rm -rf chrome.zip chromedriver.zip chrome-linux64 chromedriver-linux64

# Check installation
echo "✅ Checking Chromedriver path..."
ls -l /usr/local/bin/chromedriver || echo "❌ Chromedriver not found!"
