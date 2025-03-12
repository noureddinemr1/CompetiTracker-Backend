import requests

API_KEY = "your_firecrawl_api_key"
FIRECRAWL_MAP_URL = "https://api.firecrawl.com/v1/map"

def get_all_website_urls(base_url):
    """Uses Firecrawl 'Map' API to get all URLs of a website."""
    payload = {
        "url": base_url,
        "api_key": API_KEY
    }

    response = requests.post(FIRECRAWL_MAP_URL, json=payload)
    data = response.json()

    if response.status_code == 200 and "urls" in data:
        return data["urls"]  
    else:
        print(f"❌ Error mapping {base_url}: {data}")
        return []
