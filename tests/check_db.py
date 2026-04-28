import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI_LOCAL")
if not MONGO_URI:
    raise ValueError(" MONGO_URI_LOCAL manquant dans .env")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client[os.getenv("MONGO_DATABASE", "medical_db")]
collection = db["patients"]

print("Nombre de documents :", collection.count_documents({}))
print("Exemple de document :")
print(collection.find_one())

client.close()