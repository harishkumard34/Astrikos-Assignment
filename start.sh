#!/bin/bash

# Start the background data generator
python generator/main.py &

# Start the FastAPI backend
# Render provides the $PORT variable automatically
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
