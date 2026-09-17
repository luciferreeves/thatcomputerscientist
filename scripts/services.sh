#!/bin/bash

echo "Setting up systemd services..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SYSTEMD_DIR="$PROJECT_DIR/systemd"

if [[ ! -d "$SYSTEMD_DIR" ]]; then
    echo "Error: systemd directory not found at $SYSTEMD_DIR"
    exit 1
fi

for service_file in "$SYSTEMD_DIR"/*.service; do
    if [[ -f "$service_file" ]]; then
        service_name=$(basename "$service_file")
        echo "Processing $service_name..."
        
        sudo cp "$service_file" "/etc/systemd/system/$service_name"
        echo "Copied $service_name to /etc/systemd/system/"
    fi
done

echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

for service_file in "$SYSTEMD_DIR"/*.service; do
    if [[ -f "$service_file" ]]; then
        service_name=$(basename "$service_file" .service)
        
        if ! systemctl is-enabled "$service_name" &>/dev/null; then
            echo "Enabling $service_name..."
            sudo systemctl enable "$service_name"
        fi
        
        echo "Starting $service_name..."
        sudo systemctl restart "$service_name"
        
        if systemctl is-active "$service_name" &>/dev/null; then
            echo "✓ $service_name is running"
        else
            echo "✗ $service_name failed to start"
        fi
    fi
done

echo "Service setup complete!"