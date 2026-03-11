#!/usr/bin/env python3
"""
Auto-update script for Seattle Today dashboard
Scrapes fresh data and updates index.html
"""

import json
import re
from datetime import datetime
from pathlib import Path

# Import the scraper
import sys
sys.path.insert(0, str(Path(__file__).parent))
from scraper_working import scrape_infatuation


def update_dashboard():
    """Scrape fresh data and update index.html"""
    
    print("🥭 Updating Seattle Today dashboard...")
    
    # Scrape fresh data
    restaurants = scrape_infatuation()
    
    if not restaurants:
        print("❌ No restaurants found, aborting update")
        return False
    
    # Read current index.html
    dashboard_path = Path(__file__).parent / 'index.html'
    with open(dashboard_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Convert restaurants to JavaScript array
    restaurants_js = json.dumps(restaurants, indent=4, ensure_ascii=False)
    
    # Replace the restaurants array in the HTML
    # Find the pattern: const restaurants = [...];
    pattern = r'(const restaurants = )\[.*?\];'
    
    def replace_restaurants(match):
        return f'const restaurants = {restaurants_js};'
    
    new_html = re.sub(pattern, replace_restaurants, html, flags=re.DOTALL)
    
    # Update the lastUpdated date
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    new_html = re.sub(
        r'(<span id="lastUpdated">).*?(</span>)',
        lambda m: f'{m.group(1)}{today}{m.group(2)}',
        new_html
    )
    
    # Write updated HTML
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f"✅ Updated {len(restaurants)} restaurants")
    print(f"✅ Dashboard updated at {today}")
    return True


if __name__ == '__main__':
    try:
        success = update_dashboard()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
