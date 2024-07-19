#!/bin/sh

# Install dependencies
pip install --no-cache-dir -r /app/requirements.txt

# Start the Flask application
exec python server.py
