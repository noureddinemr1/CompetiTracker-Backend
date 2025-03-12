from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "competitracker"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def save_to_db(collection_name, data):

    collection = db[collection_name]
    if isinstance(data, list):
        collection.insert_many(data)
    else:
        collection.insert_one(data)

def update_db(collection_name,query,data):
    collection = db[collection_name]
    collection.update_many(query, {"$set": data})

def get_from_db(collection_name, query):
    collection = db[collection_name]
    document = collection.find_one(query)
    return document  

