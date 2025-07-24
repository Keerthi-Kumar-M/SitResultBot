#!/bin/bash
set -e

echo "✅ Updating packages..."
apt-get update -y
apt-get install -y wget unzip curl gnupg

CHROME_VERSION="138.0.7204.168"
BASE_URL="https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64"

echo "✅ Downloading Chrome version ${CHROME_VERSION}..."
wget "${BASE_URL}/chrome-linux64.zip" -O chrome.zip
unzip chrome.zip
mv chrome-linux64 /opt/chrome
ln -s /opt/chrome/chrome /usr/bin/google-chrome

echo "✅ Downloading Chromedriver version ${CHROME_VERSION}..."
wget "${BASE_URL}/chromedriver-linux64.zip" -O chromedriver.zip
unzip chromedriver.zip
chmod +x chromedriver-linux64/chromedriver
mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

echo "✅ Cleaning up..."
rm -rf chrome.zip chromedriver.zip chrome-linux64 chromedriver-linux64

echo "✅ Verifying Chromedriver path..."
ls -l /usr/local/bin/chromedriver || echo "❌ Chromedriver not found!"
