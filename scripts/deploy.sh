# Only to be used on the server
#!/bin/bash
echo "Starting Deployment Script"

# Move to the project directory
cd /home/ubuntu/thatcomputerscientist

# Pull the latest code
git pull --recurse-submodules

# remove the .env file
rm /home/ubuntu/thatcomputerscientist/.env

# copy the .env file
cp /home/ubuntu/.shifooenv /home/ubuntu/thatcomputerscientist/.env

# Activate venv
source /home/ubuntu/thatcomputerscientist/venv/bin/activate

# Install Deps
echo "Installing Dependencies"
pip3 install -r requirements.txt

# Compile Languages
echo "Compiling Languages"
./scripts/localegen.sh -c

# Collect Static
echo "Collecting Static Files"
python3 manage.py collectstatic --noinput

# Make Migrations
echo "Making Migrations"
python3 manage.py makemigrations

# Migrate
echo "Migrating Database"
python3 manage.py migrate

# Setup and restart services
echo "Setting up and restarting services"
./scripts/services.sh

# Extra
echo "Done. Exiting..."
exit 0