#!/bin/bash
# Auto-push to GitHub using stored credentials

cd "$(dirname "$0")"

# Load credentials from .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ No GitHub token found in .env"
    exit 1
fi

# Configure git to use token
git remote set-url origin "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/seattle-today.git" 2>/dev/null || \
git remote add origin "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/${GITHUB_USERNAME}/seattle-today.git"

echo "🚀 Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub"
    echo "📍 https://github.com/${GITHUB_USERNAME}/seattle-today"
else
    echo "❌ Push failed"
    exit 1
fi
