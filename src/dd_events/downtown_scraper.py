import json
import time
import warnings
from pathlib import Path

import httpx
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

SITEMAP_URL = "https://downtowndallas.com/tribe_events-sitemap.xml"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

def get_event_urls():
        response = httpx.get(SITEMAP_URL, headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        urls = []
        for loc in soup.find_all("loc"):
            url = loc.text
            if "/event/" in url:
                urls.append(url)
        return urls

def parse_event_page(url):
        try:
            response = httpx.get(url, headers=HEADERS)
            response.raise_for_status()
        except httpx.HTTPStatusError:
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        for script in soup.find_all("script", type="application/ld+json"):
              data=json.loads(script.string)
              items = data if isinstance(data, list) else [data]
              for item in items:
                    if item.get("@type") == "Event":
                        return item
        return None

def main():
        urls = get_event_urls()
        events = []
        for url in urls:
            event = parse_event_page(url)
            events.append(event)
            print(event)
            time.sleep(10)

        events = [e for e in events if e is not None]

        path = Path('data/raw/dd_events.json')
        path.parent.mkdir(parents=True, exist_ok=True) # makes data/raw/
        with open(path, "w", encoding="utf-8") as file:
              json.dump(events, file, indent=2)
        print('dd_events.json path:', path)
