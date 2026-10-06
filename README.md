This project scrapes Downtown Dallas' event sitemap, builds a subscription calendar, and auto-updates daily via GitHub Actions, published through GitHub Pages.

Calendar Subscription Link: https://connerhoelzle.github.io/dd-events/dd_events.ics

**
cli.py scrapes event pages and outputs dd_events.json
make_ics.py reads dd_events.json, gets and formats relevant data, and outputs docs/dd_events.ics
GitHub Pages site is built from /docs/
.github/workflows/get-events-data.yml outlines GitHub Actions workflow that auto-updates dd_events.ics, daily
**

*requires Python 3.10+ for icalendar library 
