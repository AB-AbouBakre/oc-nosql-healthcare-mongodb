from pymongo import MongoClient

MONGO_URI = "mongodb://root:rootpassword@localhost:27017/medical_db?authSource=admin"

client = MongoClient(MONGO_URI)
db = client["medical_db"]
collection = db["patients"]

print("Nombre de documents :", collection.count_documents({}))
print("Exemple de document :")
print(collection.find_one())

client.close()
