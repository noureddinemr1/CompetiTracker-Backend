from urllib.parse import urlparse
from firecrawl import FirecrawlApp
import os
import datetime


# Load API key from environment variables for security
API_KEY = "fc-b75c7ffc064941369610bec7c2227513"  # Replace this with the actual key or environment variable

def scrape_competitor(url):
    app = FirecrawlApp(api_key=API_KEY)

    params = {
    "formats": ["extract"],
    "extract": {
        "schema": {
            "name": {"type": "string"},
            "Logo Mytek": {"type": "string"},
        }
    },
    }
    response = app.scrape_url(url,params=params)

    competitor_data = {
        "name": response.get("name", "Unknown Competitor"),
        "logo": response.get("Logo Mytek", ""),
        "url": url
    }

    return competitor_data

# Example usage:
print(scrape_competitor("https://mytek.tn/"))

