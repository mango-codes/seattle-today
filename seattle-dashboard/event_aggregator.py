#!/usr/bin/env python3
"""
Seattle Event Aggregator
Scrapes events from multiple sources
"""

import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup


class EventAggregator:
    def __init__(self):
        self.events = []
    
    def scrape_stranger_things(self):
        """Scrape from Stranger Things To Do (Seattle)"""
        print("📰 Scraping Stranger Things To Do...")
        
        try:
            url = "https://www.thestranger.com/things-to-do"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            events = []
            
            # Look for event listings
            # Stranger uses article cards for events
            for article in soup.find_all('article', limit=20):
                try:
                    # Title
                    title_elem = article.find('h2') or article.find('h3')
                    if not title_elem:
                        continue
                    title = title_elem.get_text().strip()
                    
                    # Skip if too short or looks like a section header
                    if len(title) < 5 or 'calendar' in title.lower():
                        continue
                    
                    # Link
                    link_elem = article.find('a')
                    link = link_elem['href'] if link_elem else None
                    if link and not link.startswith('http'):
                        link = f"https://www.thestranger.com{link}"
                    
                    # Date/time
                    date_elem = article.find('time') or article.find(class_=lambda x: x and 'date' in x.lower())
                    date_str = date_elem.get_text().strip() if date_elem else None
                    
                    # Description
                    desc_elem = article.find('p')
                    description = desc_elem.get_text().strip()[:200] if desc_elem else None
                    
                    events.append({
                        'title': title,
                        'date': date_str,
                        'description': description,
                        'link': link,
                        'source': 'stranger_things',
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  ✓ {title[:50]}")
                    
                except Exception as e:
                    continue
            
            return events
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    def scrape_seattle_met(self):
        """Scrape from Seattle Met events"""
        print("📰 Scraping Seattle Met...")
        
        try:
            url = "https://www.seattlemet.com/arts-and-culture/events"
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            events = []
            
            # Look for event listings
            for item in soup.find_all(['article', 'div'], class_=lambda x: x and 'event' in x.lower(), limit=15):
                try:
                    title_elem = item.find('h2') or item.find('h3') or item.find('h4')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text().strip()
                    if len(title) < 5:
                        continue
                    
                    link_elem = item.find('a')
                    link = link_elem['href'] if link_elem else None
                    if link and not link.startswith('http'):
                        link = f"https://www.seattlemet.com{link}"
                    
                    date_elem = item.find('time') or item.find(class_=lambda x: x and 'date' in x.lower())
                    date_str = date_elem.get_text().strip() if date_elem else None
                    
                    events.append({
                        'title': title,
                        'date': date_str,
                        'link': link,
                        'source': 'seattle_met',
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"  ✓ {title[:50]}")
                    
                except:
                    continue
            
            return events
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return []
    
    async def scrape_eventbrite(self):
        """Scrape from Eventbrite Seattle"""
        print("📰 Scraping Eventbrite...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                # Search for Seattle events
                url = "https://www.eventbrite.com/d/wa--seattle/events/"
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(3)
                
                events = []
                
                # Eventbrite uses specific selectors
                cards = await page.query_selector_all('[data-testid="event-card"]')
                
                for card in cards[:15]:
                    try:
                        # Title
                        title_elem = await card.query_selector('h2, h3, [data-testid="event-title"]')
                        title = await title_elem.inner_text() if title_elem else None
                        
                        # Date
                        date_elem = await card.query_selector('[data-testid="event-date"]')
                        date_str = await date_elem.inner_text() if date_elem else None
                        
                        # Link
                        link_elem = await card.query_selector('a')
                        link = await link_elem.get_attribute('href') if link_elem else None
                        
                        if title and len(title) > 3:
                            events.append({
                                'title': title.strip(),
                                'date': date_str,
                                'link': link,
                                'source': 'eventbrite',
                                'scraped_at': datetime.now().isoformat()
                            })
                            print(f"  ✓ {title[:50]}")
                    except:
                        continue
                
                await browser.close()
                return events
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                await browser.close()
                return []


def main():
    print("🎭 Seattle Event Aggregator")
    print("=" * 50)
    print()
    
    aggregator = EventAggregator()
    all_events = []
    
    # Scrape from multiple sources
    all_events.extend(aggregator.scrape_stranger_things())
    print()
    
    all_events.extend(aggregator.scrape_seattle_met())
    print()
    
    # Eventbrite with Playwright
    eventbrite_events = asyncio.run(aggregator.scrape_eventbrite())
    all_events.extend(eventbrite_events)
    print()
    
    # Deduplicate by title
    seen = set()
    unique_events = []
    for event in all_events:
        key = event['title'].lower().strip()
        if key and key not in seen:
            seen.add(key)
            unique_events.append(event)
    
    # Save results
    output = {
        'scraped_at': datetime.now().isoformat(),
        'location': 'Seattle, WA',
        'count': len(unique_events),
        'events': unique_events
    }
    
    with open('seattle_events.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("=" * 50)
    print(f"✅ Found {len(unique_events)} unique events")
    print("📄 Results saved to seattle_events.json")


if __name__ == '__main__':
    main()
