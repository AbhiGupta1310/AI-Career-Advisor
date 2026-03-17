#!/bin/bash

echo "🛑 Cleaning up existing processes..."

# Kill process running on Backend port (8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Killing process on port 8000 (Backend)"
    lsof -ti:8000 | xargs kill -9
else
    echo "Port 8000 is free."
fi

# Kill process running on Frontend port (5173)
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "Killing process on port 5173 (Frontend)"
    lsof -ti:5173 | xargs kill -9
else
    echo "Port 5173 is free."
fi

echo "🚀 Starting development servers via 'make dev'..."
make dev
