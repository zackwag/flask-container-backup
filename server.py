from flask import Flask, request, jsonify
import subprocess
import json
import os

app = Flask(__name__)

# Declare constants
FLASK_PORT = 2128

# Add logic here

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=FLASK_PORT)
