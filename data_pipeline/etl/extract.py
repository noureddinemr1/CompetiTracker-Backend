from data_pipeline.scrapers.scrape_url import scrape_product_page
from data_pipeline.etl.crawler import get_all_website_urls
from data_pipeline.etl.url_utils import is_product_url

def extract_all_products(base_url):
    """Find all product URLs and scrape them."""
    all_links = get_all_website_urls(base_url)

    product_links = [url for url in all_links if is_product_url(url)]
    print(f"✅ Found {len(product_links)} valid product URLs.")

    products_data = []
    for product_url in product_links:
        data = scrape_product_page(product_url)
        if data:
            products_data.append(data)

    return products_data
