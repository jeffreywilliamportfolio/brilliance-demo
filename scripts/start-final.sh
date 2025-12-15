#!/bin/bash

# Final Brilliance Start Script
# Starts backend and provides frontend instructions

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

# Start backend in background
echo "🔌 Starting Flask backend on port 8000..."
python -c "
from dotenv import load_dotenv
load_dotenv('../.env')
from brilliance.api.v1 import app
app.run(host='0.0.0.0', port=8000, debug=True)
" &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    exit 1
fi

echo "✅ Backend started successfully (PID: $BACKEND_PID)"

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

echo ""
echo "🎉 Backend is running!"
echo "📱 Backend API: http://localhost:8000"
echo "🏥 Health check: http://localhost:8000/health"
echo ""
echo "🔧 To start the frontend, run in a new terminal:"
echo "   cd brilliance/frontend"
echo "   BROWSER=none npm start"
echo ""
echo "📱 Frontend will be available at: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the backend"

# Wait for user interrupt
wait
