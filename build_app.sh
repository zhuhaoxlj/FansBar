#!/bin/bash

# Set working directory to the script location
cd "$(dirname "$0")"

# Suppress DrissionPage's SyntaxWarning
export PYTHONWARNINGS=ignore::SyntaxWarning:DrissionPage

echo -e "\033[1;36m===== Building GetFans Menu Bar App =====\033[0m"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "\033[1;33mCreating virtual environment...\033[0m"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "\033[1;31mFailed to create virtual environment!\033[0m"
        exit 1
    fi
fi

# Activate virtual environment
echo -e "\033[1;33mActivating virtual environment...\033[0m"
source venv/bin/activate

# Install dependencies
echo -e "\033[1;33mInstalling dependencies...\033[0m"
python -m pip install --upgrade pip > /dev/null
pip install -r requirements.txt > /dev/null
pip install pyinstaller > /dev/null

# Run build script
echo -e "\033[1;33mStarting build process...\033[0m"
python build.py

# Check if build was successful
if [ -d "dist/mac/GetFans.app" ]; then
    echo -e "\033[1;32m===== Build Successful! =====\033[0m"
    
    # Ask if user wants to run the app
    read -p "Do you want to run the app now? (y/n): " choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        echo -e "\033[1;33mLaunching GetFans App...\033[0m"
        open dist/mac/GetFans.app
    fi
else
    echo -e "\033[1;31m===== Build Failed! =====\033[0m"
fi

# Deactivate virtual environment
deactivate

echo -e "\033[1;36m===== Build Process Complete =====\033[0m" 