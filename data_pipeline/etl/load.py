import json
from data_pipeline.storage.database import save_to_db

def save_to_json(data, filename):
    """Saves scraped data to a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"📂 Data saved to {filename}")

def load_into_database(data):
    """Saves product data into the database."""
    save_to_db("products", data)
    print("✅ Data successfully stored in the database.")
