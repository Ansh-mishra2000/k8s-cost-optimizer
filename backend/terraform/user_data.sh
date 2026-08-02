#!/bin/bash

# Update package list
apt-get update -y

# Install Nginx
apt-get install -y nginx

# Enable Nginx to start on boot
systemctl enable nginx

# Start Nginx
systemctl start nginx