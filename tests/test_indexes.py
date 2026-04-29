import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI_LOCAL")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI_LOCAL manquant dans .env")

client = MongoClient(MONGO_URI)
db = client[os.getenv("MONGO_DATABASE", "medical_db")]
collection = db["patients"]

print("\n🧪 Test des performances avec EXPLAIN\n")
print("=" * 60)

# Test 1 : Recherche par Hospital
print("\n1️⃣  Recherche par Hospital")
explain = collection.find({"Hospital": "Sons and Miller"}).explain()
stage = explain['executionStats']['executionStages']['stage']
docs_examined = explain['executionStats']['totalDocsExamined']
docs_returned = explain['executionStats']['nReturned']
time_ms = explain['executionStats']['executionTimeMillis']

print(f"   Stratégie : {stage}")
print(f"   Documents scannés : {docs_examined}")
print(f"   Documents retournés : {docs_returned}")
print(f"   Temps : {time_ms} ms")
print(f"   {'✅ Index utilisé' if stage == 'IXSCAN' or stage == 'FETCH' else '❌ Pas d\'index (COLLSCAN)'}")

# Test 2 : Tri par Date of Admission
print("\n2️⃣  Tri par Date of Admission (10 plus récents)")
explain = collection.find().sort("Date of Admission", -1).limit(10).explain()
stage = explain['executionStats']['executionStages']['stage']
time_ms = explain['executionStats']['executionTimeMillis']
print(f"   Stratégie : {stage}")
print(f"   Temps : {time_ms} ms")
print(f"   {'✅ Index utilisé' if 'IXSCAN' in str(explain) else '❌ Pas d\'index'}")

# Test 3 : Recherche par Medical Condition
print("\n3️⃣  Recherche par Medical Condition (Cancer)")
explain = collection.find({"Medical Condition": "Cancer"}).explain()
stage = explain['executionStats']['executionStages']['stage']
docs_examined = explain['executionStats']['totalDocsExamined']
docs_returned = explain['executionStats']['nReturned']
time_ms = explain['executionStats']['executionTimeMillis']
print(f"   Stratégie : {stage}")
print(f"   Documents scannés : {docs_examined}")
print(f"   Documents retournés : {docs_returned}")
print(f"   Temps : {time_ms} ms")
print(f"   {'✅ Index utilisé' if stage == 'IXSCAN' or stage == 'FETCH' else '❌ Pas d\'index'}")

# Test 4 : Requête composée Hospital + Date
print("\n4️⃣  Hospital + tri Date (index composé)")
explain = collection.find({"Hospital": "Sons and Miller"}).sort("Date of Admission", -1).explain()
stage = explain['executionStats']['executionStages']['stage']
time_ms = explain['executionStats']['executionTimeMillis']
print(f"   Stratégie : {stage}")
print(f"   Temps : {time_ms} ms")
print(f"   {'✅ Index composé utilisé' if 'IXSCAN' in str(explain) else '❌ Pas d\'index'}")

# Test 5 : Recherche par Admission Type
print("\n5️⃣  Recherche par Admission Type (Emergency)")
explain = collection.find({"Admission Type": "Emergency"}).explain()
stage = explain['executionStats']['executionStages']['stage']
docs_examined = explain['executionStats']['totalDocsExamined']
docs_returned = explain['executionStats']['nReturned']
time_ms = explain['executionStats']['executionTimeMillis']
print(f"   Stratégie : {stage}")
print(f"   Documents scannés : {docs_examined}")
print(f"   Documents retournés : {docs_returned}")
print(f"   Temps : {time_ms} ms")
print(f"   {'✅ Index utilisé' if stage == 'IXSCAN' or stage == 'FETCH' else '❌ Pas d\'index'}")

print("\n" + "=" * 60)
print("\n📋 Liste des index créés :")
for idx in collection.list_indexes():
    print(f"   • {idx['name']}")

nb_docs = collection.count_documents({})
print(f"\n📊 Nombre total de documents : {nb_docs}")

client.close()
print("\n✅ Tests terminés\n")