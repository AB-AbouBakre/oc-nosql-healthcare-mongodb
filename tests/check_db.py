from pymongo import MongoClient

# URI alignée avec ta config actuelle (user root-oc, mot de passe fort)
MONGO_URI = (
    "mongodb://root-oc:vQ7nZ3pL9r_cT2X"
    "@localhost:27017/medical_db?authSource=admin"
)

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
db = client["medical_db"]
collection = db["patients"]  # adapte si le nom de ta collection est différent

print("Nombre de documents :", collection.count_documents({}))
print("Exemple de document :")
print(collection.find_one())

client.close()