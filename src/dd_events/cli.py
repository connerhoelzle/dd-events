import warnings
import time
import json
import httpx
from bs4 import BeautifulSoup
from bs4 import XMLParsedAsHTMLWarning

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
            soup = BeautifulSoup(response.text, "html.parser")
        except httpx.HTTPStatusError:
            return None

        for script in soup.find_all("script", type="application/ld+json"):
              data=json.loads(script.string)
              items = data if isinstance(data, list) else [data]
              for item in items:
                    if item.get("@type") == "Event":
                          return {
                                "title": item.get("name"),
                                "start": item.get("startDate"),
                                "end": item.get("endDate"),
                                "url": item.get("url", url),
                          }
        return None

def main():
      urls = get_event_urls()
      for url in urls:
            event = parse_event_page(url)
            print(event)
            time.sleep(0.5)