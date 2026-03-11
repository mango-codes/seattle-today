#!/usr/bin/env python3
"""
Restaurant Availability Agent v2
Direct navigation to restaurant pages
"""

import asyncio
import json
from datetime import datetime, timedelta
from playwright.async_api import async_playwright


class AvailabilityAgent:
    def __init__(self):
        self.results = []
    
    async def check_opentable_restaurant(self, restaurant_slug, party_size=2):
        """
        Check availability on OpenTable using direct restaurant URL
        restaurant_slug: e.g., "din-tai-fung-seattle" or "din-tai-fung-pacific-place"
        """
        
        print(f"🔍 Checking OpenTable for: {restaurant_slug}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-http2']  # Try disabling HTTP2
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 800}
            )
            page = await context.new_page()
            
            try:
                # Go directly to restaurant page
                url = f"https://www.opentable.com/r/{restaurant_slug}"
                print(f"  Navigating to: {url}")
                
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(3)
                
                # Take screenshot for debugging
                await page.screenshot(path=f'debug_{restaurant_slug}.png')
                
                # Check if we hit a captcha or error page
                content = await page.content()
                if 'captcha' in content.lower() or 'access denied' in content.lower():
                    print(f"  ❌ Blocked by captcha")
                    await browser.close()
                    return None
                
                print(f"  ✓ Page loaded")
                
                # Look for party size selector
                party_selectors = [
                    'select[data-test="party-size-select"]',
                    'select[name="partySize"]',
                    '[data-testid="party-size-select"]',
                    'select[aria-label*="party" i]',
                ]
                
                party_selected = False
                for selector in party_selectors:
                    try:
                        party_dropdown = await page.wait_for_selector(selector, timeout=5000)
                        if party_dropdown:
                            await party_dropdown.select_option(str(party_size))
                            party_selected = True
                            print(f"  ✓ Set party size to {party_size}")
                            await asyncio.sleep(1)
                            break
                    except:
                        continue
                
                # Look for date picker
                today = datetime.now()
                
                # Try clicking on date field
                date_selectors = [
                    '[data-test="date-picker"]',
                    '[data-testid="date-picker"]',
                    'button[aria-label*="date" i]',
                    'input[placeholder*="Date" i]',
                ]
                
                for selector in date_selectors:
                    try:
                        date_elem = await page.wait_for_selector(selector, timeout=5000)
                        if date_elem:
                            await date_elem.click()
                            await asyncio.sleep(1)
                            # Look for today
                            today_btn = await page.query_selector('button:has-text("Today"), [data-date]')
                            if today_btn:
                                await today_btn.click()
                                print(f"  ✓ Selected today's date")
                                await asyncio.sleep(2)
                                break
                    except:
                        continue
                
                # Look for available times
                print(f"  Looking for available times...")
                time_slots = []
                
                # Wait a bit for times to load
                await asyncio.sleep(3)
                
                # Try multiple selectors for time buttons
                time_selectors = [
                    'button[data-testid*="time"]',
                    '[data-test="time-slot"]',
                    'button:has-text(":")',
                    '.time-slot button',
                    '[role="button"]',
                ]
                
                for selector in time_selectors:
                    buttons = await page.query_selector_all(selector)
                    for btn in buttons[:15]:
                        try:
                            text = await btn.inner_text()
                            text = text.strip()
                            # Filter for time-looking strings
                            if any(c in text for c in [':', 'AM', 'PM']) and len(text) < 15:
                                if text not in time_slots:
                                    time_slots.append(text)
                        except:
                            continue
                
                result = {
                    'restaurant_slug': restaurant_slug,
                    'platform': 'OpenTable',
                    'party_size': party_size,
                    'date': today.strftime('%Y-%m-%d'),
                    'available_times': time_slots[:8],
                    'has_availability': len(time_slots) > 0,
                    'checked_at': datetime.now().isoformat()
                }
                
                if time_slots:
                    print(f"  ✅ Found {len(time_slots)} times: {', '.join(time_slots[:5])}")
                else:
                    print(f"  ⚠️ No times found (may need different approach)")
                
                await browser.close()
                return result
                
            except Exception as e:
                print(f"  ❌ Error: {str(e)[:100]}")
                await browser.close()
                return {
                    'restaurant_slug': restaurant_slug,
                    'platform': 'OpenTable',
                    'error': str(e)[:200],
                    'checked_at': datetime.now().isoformat()
                }


async def main():
    """Test the availability agent"""
    
    print("🥭 Restaurant Availability Agent v2")
    print("=" * 50)
    print()
    
    agent = AvailabilityAgent()
    
    # Test with known OpenTable slugs
    # These need to be discovered - they're usually the restaurant name with hyphens
    restaurants = [
        "din-tai-fung-pacific-place",  # Din Tai Fung at Pacific Place
        "din-tai-fung-university-village",  # Alternative location
    ]
    
    results = []
    
    for restaurant in restaurants:
        result = await agent.check_opentable_restaurant(restaurant, party_size=2)
        if result:
            results.append(result)
        print()
        await asyncio.sleep(3)
    
    # Save results
    output = {
        'checked_at': datetime.now().isoformat(),
        'location': 'Seattle, WA',
        'results': results
    }
    
    with open('availability_v2.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("=" * 50)
    print(f"✅ Checked {len(results)} restaurants")
    print("📄 Results saved to availability_v2.json")


if __name__ == '__main__':
    asyncio.run(main())
