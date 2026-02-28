#!/bin/bash

echo "🚀 Starting Termux Setup for Shein Checker..."

# 1. Check if Python and Nano are installed
if ! command -v python &> /dev/null || ! command -v nano &> /dev/null; then
    echo "📦 Updating packages and installing Python & Nano..."
    pkg update -y && pkg upgrade -y
    pkg install python nano -y
else
    echo "✅ Python & Nano already installed. Skipping update..."
fi

# 2. Check if requests library is installed
if ! python -c "import requests" &> /dev/null; then
    echo "🐍 Installing requests library..."
    pip install requests
else
    echo "✅ Requests library already installed. Skipping..."
fi

# 3. Enable wake-lock (Phone sleep disable)
echo "🔒 Enabling termux-wake-lock to prevent sleep..."
termux-wake-lock

# 4. Create necessary files automatically if they don't exist
echo "📁 Checking and creating required files..."
touch cookies.json
touch vouchers.txt
touch valid_vouchers.txt

echo "================================================="
echo "✅ Setup Ready!"
echo "⚠️ DHYAN DEIN: Agar aapne abhi tak cookies.json aur vouchers.txt me apna data nahi dala hai, toh script error degi ya 'No vouchers found' bolegi."
echo "================================================="
echo "▶️ Running the Python script in 3 seconds..."
sleep 3

# 5. Run the main python script
python ashu.py