#!/usr/bin/env python3
"""
Seattle Event Aggregator - Clean version
Focus on Songkick for reliable concert data
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
        
        # Find all event rows
        for row in soup.find_all('li', class_=lambda x: x and 'concert' in str(x).lower()):
            try:
                # Artist name - look for the main link
                artist_link = row.find('a', href=lambda x: x and '/concerts/' in x)
                artist = artist_link.get_text().strip() if artist_link else None
                
                # Venue
                venue_link = row.find('a', href=lambda x: x and '/venues/' in x)
                venue = venue_link.get_text().strip() if venue_link else None
                
                # Date
                date_elem = row.find('time')
                date_str = None
                if date_elem:
                    datetime_attr = date_elem.get('datetime')
                    if datetime_attr:
                        date_str = datetime_attr[:10]  # YYYY-MM-DD
                    else:
                        date_str = date_elem.get_text().strip()
                
                # Link
                link = None
                if artist_link:
                    href = artist_link.get('href')
                    if href:
                        link = f"https://www.songkick.com{href}"
                
                if artist:
                    # Clean up the data
                    artist = artist.replace('\n', ' ').strip()
                    venue = venue.replace('\n', ' ').strip() if venue else None
                    
                    events.append({
                        'title': f"{artist} at {venue}" if venue else artist,
                        'artist': artist,
                        'venue': venue,
                        'date': date_str,
                        'link': link,
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
    
    with open('seattle_events_clean.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print()
    print(f"✅ Saved {len(events)} events")
    
    # Show upcoming
    print("\n📅 Upcoming concerts:")
    for e in events[:10]:
        date = e.get('date', 'TBD')
        title = e.get('title', 'Unknown')[:50]
        print(f"  {date} - {title}")


if __name__ == '__main__':
    main()
