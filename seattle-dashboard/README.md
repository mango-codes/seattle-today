# 🥭 Seattle Today

A dashboard showing the best restaurants in Seattle right now.

## What's This?

A simple, daily-updated dashboard that aggregates Seattle's top restaurants from curated sources. Currently pulls from The Infatuation's Top 25 Seattle restaurants.

## Features

- **25 curated restaurants** with cuisine, neighborhood, and vibe tags
- **Filter by** neighborhood, cuisine, or search by name
- **Quick actions** — Find a table (OpenTable) or get directions (Google Maps)
- **Mobile-friendly** responsive design

## Quick Start

```bash
cd seattle-dashboard
./serve.sh
# Open http://localhost:8080
```

## Auto-Refresh

The dashboard auto-updates daily at 6 AM Pacific via cron job.

**Manual update:**
```bash
./update-and-commit.sh
```

**Update without committing:**
```bash
source venv/bin/activate
python update_dashboard.py
```

## Data Pipeline

1. **Scrape** — `scraper_working.py` pulls data from The Infatuation
2. **Process** — Extracts names, cuisine, neighborhood, tags
3. **Update** — `update_dashboard.py` updates `index.html` automatically
4. **Display** — Static HTML dashboard with filters

## Future Improvements

- [x] Auto-refresh data via cron (runs daily at 6 AM PT)
- [ ] Add real-time reservation availability
- [ ] Weather integration (suggest indoor/outdoor)
- [ ] Add events/concerts section
- [ ] User favorites/bookmarks
- [ ] More data sources (Eater, Seattle Met, etc.)

## Files

- `index.html` — The dashboard (self-contained, no build step)
- `scraper_working.py` — Restaurant data scraper
- `update_dashboard.py` — Auto-update script for index.html
- `update-and-commit.sh` — Manual update + git commit
- `seattle_restaurants.json` — Raw scraped data
- `serve.sh` — Local development server

## Data Source

Restaurant data from [The Infatuation Seattle](https://www.theinfatuation.com/seattle/guides/best-restaurants-seattle).
