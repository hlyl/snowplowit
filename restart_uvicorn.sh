#!/bin/bash

# Find and kill the existing uvicorn process
uvicorn_pid=$(pgrep -f "uvicorn")
if [ ! -z "$uvicorn_pid" ]; then
  echo "Stopping uvicorn process with PID $uvicorn_pid"
  kill $uvicorn_pid
  sleep 2
fi

# Start a new uvicorn process
echo "Starting uvicorn process"
uvicorn main:app --reload
