#!/bin/bash
set -e

# Update and install dependencies
apt-get update -y
apt-get install -y wget unzip

# Download and install Chrome stable
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Get Chrome version (e.g. 138.0.7204.168)
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')

# Download matching Chromedriver
wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip

# Move Chromedriver to /usr/local/bin
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# Run your Python bot script
python3 SitResultResponse.py
