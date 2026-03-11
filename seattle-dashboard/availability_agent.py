#!/usr/bin/env python3
"""
Restaurant Availability Agent
Uses Playwright to check real-time availability on booking platforms
"""

import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright


class AvailabilityAgent:
    def __init__(self):
        self.results = []
    
    async def check_opentable(self, restaurant_name, party_size=2):
        """Check availability on OpenTable for a specific restaurant"""
        
        print(f"🔍 Checking OpenTable for: {restaurant_name}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                # Navigate to OpenTable
                await page.goto('https://www.opentable.com', wait_until='networkidle')
                await asyncio.sleep(2)
                
                # Search for restaurant
                search_input = await page.wait_for_selector('input[placeholder*="Search"], input[data-test="search-input"]', timeout=10000)
                await search_input.fill(f"{restaurant_name} Seattle")
                await asyncio.sleep(1)
                
                # Click search or press enter
                await search_input.press('Enter')
                await asyncio.sleep(3)
                
                # Look for restaurant in results
                # Try to find a link with the restaurant name
                restaurant_link = await page.query_selector(f'a:has-text("{restaurant_name}")')
                
                if not restaurant_link:
                    # Try partial match
                    links = await page.query_selector_all('a')
                    for link in links:
                        text = await link.inner_text()
                        if restaurant_name.lower() in text.lower() and 'seattle' in text.lower():
                            restaurant_link = link
                            break
                
                if not restaurant_link:
                    print(f"  ❌ Restaurant not found: {restaurant_name}")
                    await browser.close()
                    return None
                
                # Click on restaurant
                await restaurant_link.click()
                await asyncio.sleep(3)
                
                # Now we're on the restaurant page
                # Look for party size selector
                party_selectors = [
                    'select[data-test="party-size-select"]',
                    'select[name="partySize"]',
                    '[data-testid="party-size-select"]',
                ]
                
                party_selected = False
                for selector in party_selectors:
                    try:
                        party_dropdown = await page.wait_for_selector(selector, timeout=5000)
                        if party_dropdown:
                            await party_dropdown.select_option(str(party_size))
                            party_selected = True
                            print(f"  ✓ Set party size to {party_size}")
                            break
                    except:
                        continue
                
                if not party_selected:
                    print(f"  ⚠️ Could not set party size")
                
                await asyncio.sleep(2)
                
                # Look for date picker and select today
                today = datetime.now()
                date_str = today.strftime('%Y-%m-%d')
                
                # Try to find and click date picker
                date_pickers = [
                    '[data-test="date-picker"]',
                    '[data-testid="date-picker"]',
                    'input[type="date"]',
                    'button[aria-label*="date" i]',
                ]
                
                date_selected = False
                for selector in date_pickers:
                    try:
                        date_elem = await page.wait_for_selector(selector, timeout=5000)
                        if date_elem:
                            await date_elem.click()
                            await asyncio.sleep(1)
                            # Try to select today's date
                            today_button = await page.query_selector(f'[data-date="{date_str}"], [aria-label*="Today"], button:has-text("Today")')
                            if today_button:
                                await today_button.click()
                                date_selected = True
                                print(f"  ✓ Selected date: {today.strftime('%A, %B %d')}")
                                break
                    except:
                        continue
                
                if not date_selected:
                    print(f"  ⚠️ Could not select date, checking current view")
                
                await asyncio.sleep(3)
                
                # Look for available times
                time_slots = []
                
                # Various selectors for time slots
                time_selectors = [
                    '[data-test="time-slot"]',
                    '[data-testid="time-slot"]',
                    'button[data-testid*="time"]',
                    '.time-slot',
                    'button:has-text(":")',  # Buttons with times like "7:00"
                ]
                
                for selector in time_selectors:
                    slots = await page.query_selector_all(selector)
                    for slot in slots[:10]:  # Limit to first 10
                        try:
                            time_text = await slot.inner_text()
                            time_text = time_text.strip()
                            # Check if it looks like a time
                            if ':' in time_text or any(x in time_text for x in ['AM', 'PM', 'am', 'pm']):
                                if time_text not in time_slots:
                                    time_slots.append(time_text)
                        except:
                            continue
                
                result = {
                    'restaurant': restaurant_name,
                    'platform': 'OpenTable',
                    'party_size': party_size,
                    'date': today.strftime('%Y-%m-%d'),
                    'available_times': time_slots[:6],  # Top 6 times
                    'has_availability': len(time_slots) > 0,
                    'checked_at': datetime.now().isoformat()
                }
                
                if time_slots:
                    print(f"  ✅ Found {len(time_slots)} available times: {', '.join(time_slots[:5])}")
                else:
                    print(f"  ❌ No availability found")
                
                await browser.close()
                return result
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                await browser.close()
                return {
                    'restaurant': restaurant_name,
                    'platform': 'OpenTable',
                    'error': str(e),
                    'checked_at': datetime.now().isoformat()
                }
    
    async def check_resy(self, restaurant_name, party_size=2):
        """Check availability on Resy (stub for now)"""
        print(f"🔍 Checking Resy for: {restaurant_name}")
        # Resy is harder - requires login for most actions
        # Would need similar Playwright automation
        return {
            'restaurant': restaurant_name,
            'platform': 'Resy',
            'note': 'Resy check not yet implemented',
            'checked_at': datetime.now().isoformat()
        }


async def main():
    """Test the availability agent"""
    
    print("🥭 Restaurant Availability Agent")
    print("=" * 50)
    print()
    
    agent = AvailabilityAgent()
    
    # Test restaurants
    restaurants = [
        "Din Tai Fung",
        "Pablo y Pablo",
        # "Grappa"  # Skip for now, test with 2 first
    ]
    
    results = []
    
    for restaurant in restaurants:
        result = await agent.check_opentable(restaurant, party_size=2)
        if result:
            results.append(result)
        print()
        await asyncio.sleep(2)  # Be nice to the servers
    
    # Save results
    output = {
        'checked_at': datetime.now().isoformat(),
        'location': 'Seattle, WA',
        'party_size': 2,
        'results': results
    }
    
    with open('availability_test.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 50)
    print(f"✅ Checked {len(results)} restaurants")
    print("📄 Results saved to availability_test.json")


if __name__ == '__main__':
    asyncio.run(main())
