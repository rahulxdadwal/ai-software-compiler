#!/bin/bash
# AI Platform Compiler — Start both backend and frontend

set -e

echo "🚀 Starting AI Platform Compiler..."

# Copy .env if not present
if [ ! -f .env ]; then
    cp .env.example .env
    echo "📋 Created .env from .env.example (mock mode enabled)"
fi

# Start backend
echo "🔧 Starting backend on http://localhost:8000 ..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
else
    . venv/bin/activate
fi
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "🎨 Starting frontend on http://localhost:3000 ..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Both servers running:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

# Handle shutdown
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
