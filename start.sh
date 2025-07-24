#!/bin/bash
set -e

# Install dependencies
apt-get update -y
apt-get install -y wget unzip curl gnupg

# Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Get Chrome version
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
echo "✅ Detected Chrome version: $CHROME_VERSION"

# Download matching Chromedriver
wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" -O chromedriver.zip
unzip chromedriver.zip

# Move to correct path
chmod +x chromedriver-linux64/chromedriver
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# Confirm install
echo "✅ Checking Chromedriver path..."
ls -l /usr/local/bin/chromedriver || echo "❌ Chromedriver not found!"

# Clean up
rm -f google-chrome-stable_current_amd64.deb chromedriver.zip
rm -rf chromedriver-linux64
