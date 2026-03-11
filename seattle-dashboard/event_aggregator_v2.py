#!/usr/bin/env python3
"""
Seattle Event Aggregator v2
Focus on scrapable sources
"""

import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import re


class EventAggregator:
    def __init__(self):
        self.events = []
    
    def scrape_songkick(self):
        """Scrape concerts from Songkick Seattle"""
        print("🎵 Scraping Songkick (concerts)...")
        
        try:
            # Songkick Seattle metro area
            url = "https://www.songkick.com/metro-areas/2846-us-seattle"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            events = []
            
            # Songkick uses specific class names for events
            for event in soup.find_all('li', class_=lambda x: x and 'event' in str(x).lower()):
                try:
                    # Get artist/band name
                    artist_elem = event.find('p', class_=lambda x: x and 'artists' in str(x).lower())
                    if not artist_elem:
                        artist_elem = event.find('strong') or event.find('a')
                    
                    artist = artist_elem.get_text().strip() if artist_elem else None
                    
                    # Get venue
                    venue_elem = event.find('a', href=lambda x: x and 'venue' in str(x).lower())
                    venue = venue_elem.get_text().strip() if venue_elem else None
                    
                    # Get date
                    date_elem = event.find('time')
                    date_str = date_elem.get_text().strip() if date_elem else None
                    if not date_str:
                        date_elem = event.find(class_=lambda x: x and 'date' in str(x).lower())
                        date_str = date_elem.get_text().strip() if date_elem else None
                    
                    # Get link
                    link_elem = event.find('a', href=lambda x: x and 'concerts' in str(x).lower())
                    link = link_elem['href'] if link_elem else None
                    if link and not link.startswith('http'):
                        link = f"https://www.songkick.com{link}"
                    
                    if artist and len(artist) > 2:
                        events.append({
                            'title': f"{artist} at {venue}" if venue else artist,
                            'artist': artist,
                            'venue': venue,
                            'date': date_str,
                            'link': link,
                            'category': 'Music/Concert',
                            'source': 'songkick',
                            'scraped_at': datetime.now().isoformat()
                        })
                        print(f"  ✓ {artist[:40]} at {venue[:30] if venue else 'TBA'}")
                        
                except Exception as e:
                    continue
            
            return events
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    def scrape_reddit_seattle(self):
        """Scrape events from r/Seattle"""
        print("📱 Scraping r/Seattle...")
        
        try:
            # Reddit's JSON API is actually pretty open
            url = "https://www.reddit.com/r/Seattle/search.json?q=event&sort=new&limit=20"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            
            data = resp.json()
            events = []
            
            for post in data.get('data', {}).get('children', []):
                post_data = post.get('data', {})
                title = post_data.get('title', '')
                
                # Filter for event-related posts
                if any(word in title.lower() for word in ['event', 'concert', 'show', 'festival', 'meetup', 'happening']):
                    events.append({
                        'title': title[:100],
                        'description': post_data.get('selftext', '')[:200],
                        'link': f"https://reddit.com{post_data.get('permalink', '')}",
                        'date': datetime.fromtimestamp(post_data.get('created_utc', 0)).strftime('%Y-%m-%d'),
                        'category': 'Community',
                        'source': 'reddit_seattle',
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  ✓ {title[:50]}")
            
            return events
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    async def scrape_bandsintown(self):
        """Scrape from Bandsintown"""
        print("🎸 Scraping Bandsintown...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                url = "https://www.bandsintown.com/?place_id=ChIJVTPokywQkFQRmtVEaUZlJRA"
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(3)
                
                events = []
                
                # Look for event cards
                cards = await page.query_selector_all('[data-testid="event-card"], .event-card, [class*="event"]')
                
                for card in cards[:15]:
                    try:
                        # Artist name
                        artist_elem = await card.query_selector('h2, h3, [class*="artist"], [class*="title"]')
                        artist = await artist_elem.inner_text() if artist_elem else None
                        
                        # Venue
                        venue_elem = await card.query_selector('[class*="venue"], [class*="location"]')
                        venue = await venue_elem.inner_text() if venue_elem else None
                        
                        # Date
                        date_elem = await card.query_selector('[class*="date"], time')
                        date_str = await date_elem.inner_text() if date_elem else None
                        
                        if artist:
                            events.append({
                                'title': f"{artist} at {venue}" if venue else artist,
                                'artist': artist,
                                'venue': venue,
                                'date': date_str,
                                'category': 'Music/Concert',
                                'source': 'bandsintown',
                                'scraped_at': datetime.now().isoformat()
                            })
                            print(f"  ✓ {artist[:40]}")
                    except:
                        continue
                
                await browser.close()
                return events
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                await browser.close()
                return []


def main():
    print("🎭 Seattle Event Aggregator v2")
    print("=" * 50)
    print()
    
    aggregator = EventAggregator()
    all_events = []
    
    # Scrape from multiple sources
    all_events.extend(aggregator.scrape_songkick())
    print()
    
    all_events.extend(aggregator.scrape_reddit_seattle())
    print()
    
    # Bandsintown with Playwright
    bandsintown_events = asyncio.run(aggregator.scrape_bandsintown())
    all_events.extend(bandsintown_events)
    print()
    
    # Deduplicate by title
    seen = set()
    unique_events = []
    for event in all_events:
        key = event.get('title', '').lower().strip()[:50]
        if key and key not in seen:
            seen.add(key)
            unique_events.append(event)
    
    # Sort by date if possible
    def sort_key(e):
        date_str = e.get('date', '')
        if date_str:
            try:
                # Try to parse various date formats
                return datetime.now().strftime('%Y-%m-%d')
            except:
                pass
        return '9999-99-99'
    
    unique_events.sort(key=sort_key)
    
    # Save results
    output = {
        'scraped_at': datetime.now().isoformat(),
        'location': 'Seattle, WA',
        'count': len(unique_events),
        'events': unique_events
    }
    
    with open('seattle_events_v2.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("=" * 50)
    print(f"✅ Found {len(unique_events)} unique events")
    print("📄 Results saved to seattle_events_v2.json")
    
    # Print sample
    print("\n📋 Sample events:")
    for e in unique_events[:5]:
        print(f"  • {e.get('title', 'Unknown')[:60]}")


if __name__ == '__main__':
    main()
