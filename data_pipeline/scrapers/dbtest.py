from bson import ObjectId
from pymongo import MongoClient

client = MongoClient("mongodb+srv://noureddinemarzougui19:Fakeprofile123*@cluster0.tx9muur.mongodb.net/")
db = client["CompetiTracker"]  # Replace with your DB name

# Replace with your actual collection name
collection = db["product_history"]

# ID to match
competitor_id = ObjectId("68010009ded195a9348bea4f")

# Delete all matching documents
result = collection.delete_many({"competitor": competitor_id})

print(f"{result.deleted_count} documents deleted.")