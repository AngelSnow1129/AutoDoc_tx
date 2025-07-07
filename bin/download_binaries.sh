#!/bin/bash

# Download chrome-headless-shell
CHROME_URL="https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.92/linux64/chrome-headless-shell-linux64.zip"
CHROME_ZIP="chrome-headless-shell-linux64.zip"
CHROME_DIR="chrome-headless-shell-linux64"

wget -q --show-progress $CHROME_URL -O $CHROME_ZIP
unzip -q $CHROME_ZIP
rm $CHROME_ZIP

# Download chromedriver
CHROMEDRIVER_URL="https://storage.googleapis.com/chrome-for-testing-public/138.0.7204.92/linux64/chromedriver-linux64.zip"
CHROMEDRIVER_ZIP="chromedriver-linux64.zip"
CHROMEDRIVER_DIR="chromedriver-linux64"

wget -q --show-progress $CHROMEDRIVER_URL -O $CHROMEDRIVER_ZIP
unzip -q $CHROMEDRIVER_ZIP
rm $CHROMEDRIVER_ZIP

echo "Binaries downloaded and extracted to $CHROME_DIR and $CHROMEDRIVER_DIR"
