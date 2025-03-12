import re

def is_product_url(url):
    """Check if a URL is a product page based on structure."""
    pattern = r"^https:\/\/www\.mytek\.tn\/[^\/]+\.html$"  # Only one '/' after domain
    min_length = len("https://www.mytek.tn/chaudiere-chaffoteaux-mixte-.html")  

    return bool(re.match(pattern, url)) and len(url) >= min_length
