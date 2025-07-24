#!/bin/bash
set -e

apt-get update -y
apt-get install -y wget unzip

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get install -y ./google-chrome-stable_current_amd64.deb

CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+')

wget "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip"
unzip chromedriver-linux64.zip

# Find and move chromedriver to /usr/local/bin, handling possible folder structure
if [ -f ./chromedriver ]; then
    mv chromedriver /usr/local/bin/chromedriver
elif [ -f ./chromedriver-linux64/chromedriver ]; then
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver
else
    echo "Error: chromedriver binary not found after unzip."
    exit 1
fi

chmod +x /usr/local/bin/chromedriver
rm -rf google-chrome-stable_current_amd64.deb chromedriver-linux64.zip chromedriver-linux64

python3 SitResultResponse.py
