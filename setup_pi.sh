#!/bin/bash

# Setup script for Raspberry Pi
# Run this script from the directory containing the matrix_telnet folder

SERVICE_NAME="matrix-telnet"
PROJECT_DIR="$(pwd)"
PYTHON_PATH="$(which python3)"
PORT=2772

echo "Setting up $SERVICE_NAME on port $PORT..."

# Create the systemd service file
cat <<EOF | sudo tee /etc/systemd/system/$SERVICE_NAME.service
[Unit]
Description=Matrix ASCII Telnet Server
After=network.target

[Service]
ExecStart=$PYTHON_PATH $PROJECT_DIR/server.py
WorkingDirectory=$(pwd)
StandardOutput=inherit
StandardError=inherit
Restart=always
User=$(whoami)

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable/start the service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "Service $SERVICE_NAME installed and started!"
echo "You can check the status with: sudo systemctl status $SERVICE_NAME"
echo "To watch: telnet localhost $PORT"
