#!/bin/bash
set -e

# Update & install required packages
apt-get update -y
apt-get install -y wget unzip curl gnupg apt-transport-https software-properties-common

# Install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Extract Chrome version (major.minor.build)
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')

# Download and unzip matching ChromeDriver
wget "https://storage.googleapis.com/chrome-for-testing-public/$CHROME_VERSION/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip

# Move ChromeDriver to path and set permissions
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
chmod +x /usr/local/bin/chromedriver

# Clean up
rm -f google-chrome-stable_current_amd64.deb chromedriver-linux64.zip
rm -rf chromedriver-linux64

# Start the Python bot
python3 SitResultResponse.py
