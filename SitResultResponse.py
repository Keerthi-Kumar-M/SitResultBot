#!/bin/bash
set -e

# Update and install dependencies
apt-get update -y
apt-get install -y wget unzip

# Download and install latest stable Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

# Get Chrome major.minor.build version (e.g. 114.0.5735)
CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')

# Download matching Chromedriver from chrome-for-testing
wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip

# Move chromedriver to /usr/local/bin (adjust if inside folder)
if [ -f ./chromedriver ]; then
    mv chromedriver /usr/local/bin/chromedriver
elif [ -f ./chromedriver-linux64/chromedriver ]; then
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
else
    echo "Error: chromedriver binary not found!"
    exit 1
fi

chmod +x /usr/local/bin/chromedriver

# Clean up
rm -f google-chrome-stable_current_amd64.deb chromedriver-linux64.zip
rm -rf chromedriver-linux64
