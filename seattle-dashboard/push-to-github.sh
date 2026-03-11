#!/bin/bash
# Push to GitHub - you'll be prompted to login

cd "$(dirname "$0")"

echo "🚀 Pushing to GitHub..."
echo ""
echo "You'll be prompted to authenticate with GitHub."
echo "Choose 'Sign in with your browser' for easiest setup."
echo ""

# Set remote
git remote add origin https://github.com/mango-codes/seattle-today.git 2>/dev/null || true

# Push
git push -u origin main
