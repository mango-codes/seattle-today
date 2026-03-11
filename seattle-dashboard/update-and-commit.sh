#!/bin/bash
# Update dashboard and commit changes

cd "$(dirname "$0")"
echo "🥭 Updating Seattle Today dashboard..."

# Activate virtual environment
source venv/bin/activate

# Run update
python update_dashboard.py

if [ $? -eq 0 ]; then
    echo ""
    echo "📝 Committing changes..."
    git add index.html
    git commit -m "Update restaurant data: $(date '+%Y-%m-%d %H:%M')"
    echo "✅ Changes committed"
else
    echo "❌ Update failed, not committing"
    exit 1
fi
