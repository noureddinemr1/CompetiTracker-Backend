def transform_product_data(raw_data):
    """Cleans and formats the scraped product data."""
    transformed_data = []

    for item in raw_data:
        transformed_data.append({
            "name": item.get("title", "").strip(),
            "price": item.get("price", "").replace("TND", "").strip(),
            "availability": item.get("availability", "Unknown"),
            "description": item.get("description", "").strip(),
            "image_url": item.get("image_url", ""),
            "product_url": item.get("url", ""),
        })

    return transformed_data
