#!/bin/bash

# Set up the environment
echo "Setting up the environment..."

# Update the package list and install python3 and pip
sudo apt-get update
sudo apt-get install -y python3 python3-pip

# Install requirements from requirements.txt
pip3 install -r requirements.txt

# Run the Python script
python3 main.py

echo "Script execution completed."