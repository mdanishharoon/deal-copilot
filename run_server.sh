#!/bin/bash

# Run the FastAPI server
echo "========================================="
echo "  Deal Co-Pilot - Starting Server"
echo "========================================="
echo ""
echo "Server will be available at:"
echo "  👉 http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set Python path to project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Run the FastAPI server from project root
python -m uvicorn deal_copilot.api.main:app --host 0.0.0.0 --port 8000 --reload

