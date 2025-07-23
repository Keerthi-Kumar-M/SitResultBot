#!/bin/bash
set -e

# Install Chrome
apt-get update && apt-get install -y wget unzip gnupg curl
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Install matching Chromedriver
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')
wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip
mv chromedriver-linux64/chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver

# Start the bot
python3 SitResultResponse.py
