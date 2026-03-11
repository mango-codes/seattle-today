#!/bin/bash
# Deploy to Vercel
# Run this from the seattle-dashboard directory

cd "$(dirname "$0")"

echo "🚀 Deploying Seattle Today to Vercel..."
echo ""
echo "This will open a browser to authenticate with Vercel."
echo "If you don't have an account, you can create one for free."
echo ""
read -p "Press Enter to continue..."

npx vercel --prod
