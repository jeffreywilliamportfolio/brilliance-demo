#!/bin/bash

# Brilliance Development Start Script
# Starts both frontend and backend with proper environment setup

set -e  # Exit on any error

echo "🚀 Starting Brilliance Development Environment..."

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$DIR/.."
cd "$PROJECT_ROOT"

# Check if we're in the right directory
if [ ! -f "backend/brilliance/api/v1.py" ]; then
    echo "❌ Error: Could not verify project root."
    exit 1
fi

# Function to cleanup background processes on exit
cleanup() {
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Backend setup
echo "🔧 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install -r ../requirements.txt

# Start backend in background
echo "🔌 Starting Flask backend on port 8000..."
python3 -c "
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

# Frontend setup
echo "🔧 Setting up frontend..."
cd ../frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📥 Installing Node.js dependencies..."
    npm install
fi

# Start frontend with HOST explicitly set to localhost
echo "🔌 Starting React frontend on port 3000..."
unset HOST && npm start &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"

echo ""
echo "🎉 Brilliance is now running!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000"
echo "🏥 Health check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
wait
