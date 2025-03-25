#!/usr/bin/env python3
"""
Entry point for the Flask application.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import app after loading environment variables
from app import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
