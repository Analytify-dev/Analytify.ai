#!/bin/bash

# Prompt for email and password
read -p "Enter admin email: " ADMIN_EMAIL
read -sp "Enter admin password: " ADMIN_PASSWORD
echo

# Export the variables so they are available to Docker
export ADMIN_EMAIL=$ADMIN_EMAIL
export ADMIN_PASSWORD=$ADMIN_PASSWORD

# Run the Docker commands
docker-compose build --build-arg ADMIN_EMAIL=$ADMIN_EMAIL --build-arg ADMIN_PASSWORD=$ADMIN_PASSWORD
docker-compose up
