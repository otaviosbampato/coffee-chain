#!/bin/bash

# CoffeeChain - Startup Script (Reorganized)

echo "=================================="
echo "  CoffeeChain - Coffee Traceability"
echo "  Starting Backend & Frontend"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found!"
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install flask flask-cors pyjwt
else
    source venv/bin/activate
fi

# Create data directory if it doesn't exist
mkdir -p data

# Export secret key (change this in production!)
export SECRET_KEY='your-secret-key-change-in-production'

# Start the backend API server
echo "🚀 Starting Backend API Server..."
echo "   API will be available at: http://localhost:5000"
echo ""
cd backend/api && python3 app.py &
API_PID=$!

echo "⏳ Waiting for API server to start..."
sleep 3

# Open frontend in default browser
echo ""
echo "🌐 Opening Frontend in Browser..."
echo "   Frontend: file://$(pwd)/frontend/index.html"
echo ""

# Detect OS and open browser
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "frontend/index.html" 2>/dev/null || echo "Please open frontend/index.html manually"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open "frontend/index.html"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    start "frontend/index.html"
fi

echo ""
echo "=================================="
echo "✅ CoffeeChain is running!"
echo "=================================="
echo ""
echo "📝 Test Credentials:"
echo "   Fiscalizer: fiscalizer1 / fisc123"
echo "   Client:     client1 / client123"
echo ""
echo "🛑 To stop the server, press Ctrl+C"
echo ""

# Wait for user to stop
trap "echo ''; echo '🛑 Stopping server...'; kill $API_PID 2>/dev/null; exit" INT

wait $API_PID
