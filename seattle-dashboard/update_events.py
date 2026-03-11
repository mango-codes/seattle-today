#!/usr/bin/env python3
"""
Update events dashboard with scraped data
"""

import json
import re
from datetime import datetime
from pathlib import Path


def update_events_dashboard():
    """Inject event data into events.html"""
    
    print("🎭 Updating Seattle Tonight events...")
    
    # Load scraped events
    events_file = Path(__file__).parent / 'seattle_events.json'
    with open(events_file, 'r') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    
    if not events:
        print("❌ No events found")
        return False
    
    # Read HTML
    html_file = Path(__file__).parent / 'events.html'
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Convert events to JavaScript
    events_js = json.dumps(events, indent=4, ensure_ascii=False)
    
    # Replace the events array
    pattern = r'(const events = )\[.*?\];'
    
    def replace_events(match):
        return f'const events = {events_js};'
    
    new_html = re.sub(pattern, replace_events, html, flags=re.DOTALL)
    
    # Update last updated
    today = datetime.now().strftime('%Y-%m-%d %H:%M')
    new_html = re.sub(
        r'(<span id="lastUpdated">).*?(</span>)',
        lambda m: f'{m.group(1)}{today}{m.group(2)}',
        new_html
    )
    
    # Write updated HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(new_html)
    
    print(f"✅ Updated {len(events)} events")
    print(f"✅ Dashboard updated at {today}")
    return True


if __name__ == '__main__':
    try:
        success = update_events_dashboard()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
