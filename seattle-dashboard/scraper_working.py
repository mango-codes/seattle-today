#!/usr/bin/env python3
"""
Seattle Restaurant Scraper - Working version
Extracts The Infatuation's Top 25 Seattle restaurants
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re


def scrape_infatuation():
    """Scrape The Infatuation Seattle Top 25"""
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    url = 'https://www.theinfatuation.com/seattle/guides/best-restaurants-seattle'
    print(f"Fetching {url}...")
    
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Get all text and process line by line
    text = soup.get_text(separator='\n')
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    restaurants = []
    current = None
    
    # Known restaurant names from the page (we'll match against these)
    known_restaurants = [
        'Archipelago', 'Spinasse', 'Musang', 'Cafe Juanita', 'Kamonegi',
        'Un Bien', 'Communion R&B', 'Alebrijes Kitchen', 'Indian-Nepali Kitchen',
        'Sushi Kashiba', 'Familyfriend', 'Bar Del Corso', 'Billiard Hoang',
        'Beast & Cleaver', 'Shomon Kappo Sushi', 'Aroy Mak', 'La Cabaña',
        'Miss Pho', 'Tomo', "Lupe's Situ Tacos", 'Oriental Mart', 'Local Tide',
        'Cornelly', "Glo's", 'Lenox'
    ]
    
    neighborhoods = ['Hillman City', 'Capitol Hill', 'Beacon Hill', 'Kirkland', 
                    'Fremont', 'Ballard', 'Central District', 'Greenwood', 
                    'Pike Place Market', 'Belltown', 'Columbia City', 'White Center',
                    'Haller Lake', 'Bitter Lake']
    
    cuisines = ['Filipino', 'Italian', 'Japanese', 'Caribbean', 'Southern', 
               'Mexican', 'Indian', 'Thai', 'Latin American', 'Vietnamese',
               'American', 'Guamanian', 'Pizza', 'Steaks', 'Seafood', 'Diner',
               'Puerto Rican']
    
    tags = ['Date Nights', 'Birthdays', 'Casual Dinners', 'Special Occasions',
            'Cheap Eats', 'Lunch', 'Brunch', 'Breakfast', 'Dinner With The Parents',
            'Drinking Great Wine', 'Drinking Great Cocktails', 'Impressing Out Of Towners',
            'Fine Dining', 'Classic Establishment', 'Serious Takeout Operation',
            'Walk-Ins', 'Sitting Outside', 'Vegetarians', 'Vegans', 
            'Gluten-Free Options', 'Big Groups', 'Dining Solo', 
            'First Dates', 'Night On The Town', 'Corporate Cards',
            'Unique Dining Experiences']
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this line is a restaurant name
        # It should match one of our known restaurants
        for rest_name in known_restaurants:
            if line == rest_name or line.endswith(rest_name) or rest_name in line:
                # Check if it's not already added
                if not any(r['name'] == rest_name for r in restaurants):
                    current = {
                        'name': rest_name,
                        'address': None,
                        'cuisine': None,
                        'neighborhood': None,
                        'tags': [],
                        'source': 'infatuation_top25'
                    }
                    restaurants.append(current)
                    print(f"  ✓ {rest_name}")
                break
        
        # If we have a current restaurant, look for its details
        if current and restaurants and restaurants[-1] == current:
            # Look for address (contains Seattle)
            if 'Seattle' in line or 'Kirkland' in line:
                if not current['address'] and any(c.isdigit() for c in line):
                    current['address'] = line
            
            # Look for cuisine
            for cuisine in cuisines:
                if line == cuisine and not current['cuisine']:
                    current['cuisine'] = cuisine
            
            # Look for neighborhood
            for hood in neighborhoods:
                if line == hood and not current['neighborhood']:
                    current['neighborhood'] = hood
            
            # Look for tags
            for tag in tags:
                if line == tag and tag not in current['tags']:
                    current['tags'].append(tag)
        
        i += 1
    
    return restaurants


def save_results(restaurants):
    """Save results to JSON"""
    output = {
        'scraped_at': datetime.now().isoformat(),
        'location': 'Seattle, WA',
        'source_url': 'https://www.theinfatuation.com/seattle/guides/best-restaurants-seattle',
        'count': len(restaurants),
        'restaurants': restaurants
    }
    
    with open('seattle_restaurants.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Saved {len(restaurants)} restaurants to seattle_restaurants.json")


def main():
    print("🥭 Seattle Restaurant Scraper")
    print("=" * 40)
    
    restaurants = scrape_infatuation()
    save_results(restaurants)
    
    # Print summary
    print("\n📊 Seattle's Top Restaurants:")
    print("=" * 60)
    for i, r in enumerate(restaurants, 1):
        name = r['name']
        cuisine = f" | {r['cuisine']}" if r.get('cuisine') else ""
        neighborhood = f" | {r['neighborhood']}" if r.get('neighborhood') else ""
        tags = f" | {', '.join(r['tags'][:2])}" if r.get('tags') else ""
        print(f"  {i:2}. {name}{cuisine}{neighborhood}{tags}")


if __name__ == '__main__':
    main()
