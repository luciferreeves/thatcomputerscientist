#!/bin/bash

# Function to check if mkcert is installed
check_mkcert_installed() {
    if ! command -v mkcert &> /dev/null; then
        echo "mkcert is not installed. Installing mkcert..."
        brew install mkcert   # Assuming you're using Homebrew to install mkcert
    fi
}

# Function to check if the mkcert local CA is installed and install it if not present
check_and_install_local_ca() {
    if ! mkcert -CAROOT &> /dev/null; then
        echo "Installing mkcert local CA..."
        mkcert -install
    fi
}

# Function to set the DOMAIN value in the .env file
set_domain_in_env() {
    domain=$1
    sed -i "" "s/^DOMAIN=.*/DOMAIN='.${domain}'/" .env
}

# Function to run the development server
run_dev_server() {
    domain=$1
    cert_file="SSL/${domain}+1.pem"
    key_file="SSL/${domain}+1-key.pem"

    if [[ -f "$cert_file" && -f "$key_file" ]]; then
        set_domain_in_env "$domain"
        sudo python3 manage.py runsslserver 127.0.0.1:443 --certificate "$cert_file" --key "$key_file"
    else
        echo "Certificate files not found. Generating self-signed certificate..."
        mkdir -p SSL && cd SSL
        mkcert "${domain}" "*.${domain}"
        cd ..
        set_domain_in_env "$domain"
        sudo python3 manage.py runsslserver 127.0.0.1:443 --certificate "$cert_file" --key "$key_file"
    fi
}

# Main script

# Check if mkcert is installed and install if not present
check_mkcert_installed

# Present options to the user
echo "Choose an option:"
echo "[1]: (*).[peek].shi.foo"
echo "[2]: (*).[peek].thatcomputerscientist.com"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        domain="peek.shi.foo"
        check_and_install_local_ca
        run_dev_server "$domain"
        ;;
    2)
        domain="peek.thatcomputerscientist.com"
        check_and_install_local_ca
        run_dev_server "$domain"
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac
