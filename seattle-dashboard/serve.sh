#!/bin/bash
# Serve the dashboard locally

cd "$(dirname "$0")"
echo "🥭 Starting Seattle Today dashboard..."
echo "Open http://localhost:8080 in your browser"
echo "Press Ctrl+C to stop"
python3 -m http.server 8080
