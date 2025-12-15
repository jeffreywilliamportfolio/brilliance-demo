#!/usr/bin/env python3
"""
Brilliance Backend Server Startup Script
Run this from the backend directory: python start_server.py
"""

from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('../.env')

# Import and start the Flask app
from brilliance.api.v1 import app

if __name__ == "__main__":
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Starting Brilliance backend server on http://{host}:{port}")
    print(f"📊 Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
