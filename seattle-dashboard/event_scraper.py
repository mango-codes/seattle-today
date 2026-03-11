#!/usr/bin/env python3
"""
Seattle Event Aggregator - Working version
"""

import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup


def scrape_songkick():
    """Scrape concerts from Songkick Seattle"""
    print("🎵 Scraping Songkick...")
    
    try:
        url = "https://www.songkick.com/metro-areas/2846-us-seattle"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
        
        resp = requests.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(resp.text, 'html.parser')
        events = []
        seen = set()
        
        # Find all concert links
        for link in soup.find_all('a', href=lambda x: x and '/concerts/' in x):
            try:
                # Get the full text which includes artist and venue
                full_text = link.get_text().strip()
                
                # Split by newlines to get artist and venue
                parts = [p.strip() for p in full_text.split('\n') if p.strip()]
                
                if len(parts) >= 2:
                    artist = parts[0]
                    venue = parts[1]
                elif len(parts) == 1:
                    artist = parts[0]
                    venue = None
                else:
                    continue
                
                # Skip if we've seen this artist+venue combo
                key = f"{artist}-{venue}"
                if key in seen:
                    continue
                seen.add(key)
                
                # Get the concert URL
                href = link.get('href')
                concert_url = f"https://www.songkick.com{href}" if href else None
                
                # Try to find date nearby
                date_str = None
                parent = link.find_parent('li') or link.find_parent('div')
                if parent:
                    time_elem = parent.find('time')
                    if time_elem:
                        datetime_attr = time_elem.get('datetime')
                        if datetime_attr:
                            date_str = datetime_attr[:10]
                
                events.append({
                    'title': f"{artist} at {venue}" if venue else artist,
                    'artist': artist,
                    'venue': venue,
                    'date': date_str,
                    'link': concert_url,
                    'category': 'Music',
                    'source': 'songkick',
                    'scraped_at': datetime.now().isoformat()
                })
                
            except Exception as e:
                continue
        
        print(f"  ✓ Found {len(events)} concerts")
        return events
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return []


def main():
    print("🎭 Seattle Events")
    print("=" * 50)
    print()
    
    events = scrape_songkick()
    
    # Sort by date
    events.sort(key=lambda x: x.get('date') or '9999-99-99')
    
    # Save
    output = {
        'scraped_at': datetime.now().isoformat(),
        'location': 'Seattle, WA',
        'count': len(events),
        'events': events
    }
    
    with open('seattle_events.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print()
    print(f"✅ Saved {len(events)} events")
    
    # Show upcoming
    print("\n📅 Upcoming concerts:")
    for e in events[:10]:
        date = e.get('date', 'TBD')
        title = e.get('title', 'Unknown')[:55]
        print(f"  {date} - {title}")


if __name__ == '__main__':
    main()
