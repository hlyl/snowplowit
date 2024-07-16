#!/bin/bash

# Navigate to the src directory
cd src

# Start the first component in a new terminal window
gnome-terminal -- bash -c "streamlit run app.py; exec bash"

# Start the second component in another new terminal window
gnome-terminal -- bash -c "uvicorn main:app; exec bash"chmod +x 