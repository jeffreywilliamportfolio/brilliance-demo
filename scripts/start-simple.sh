#!/bin/bash

# Simple Brilliance Start Script
# Uses concurrently to run both services

echo "🚀 Starting Brilliance..."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$DIR/.."
cd "$PROJECT_ROOT"

# Check if we're in the right directory
if [ ! -f "backend/brilliance/api/v1.py" ]; then
    echo "❌ Error: Could not verify project root."
    exit 1
fi

# Setup backend
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment and install deps
source venv/bin/activate
pip install -r ../requirements.txt

# Go back to root
cd ..

# Setup frontend
echo "🔧 Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "📥 Installing Node.js dependencies..."
    npm install
fi
cd ..

# Start both services with concurrently
echo "🎉 Starting both services..."
npx -y concurrently -k -r -n FRONTEND,BACKEND -c blue,green \
  "cd frontend && unset HOST && npm start" \
  "cd backend && source venv/bin/activate && python -c \"from dotenv import load_dotenv; load_dotenv('../.env'); from brilliance.api.v1 import app; app.run(host='0.0.0.0', port=8000, debug=True)\""
