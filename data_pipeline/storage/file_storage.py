import json
import os

DATA_DIR = "data_pipeline/storage/"

def save_to_file(data, filename):
    """Saves data to a file in the storage directory."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    with open(os.path.join(DATA_DIR, filename), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"📂 Data saved in {DATA_DIR}{filename}")
