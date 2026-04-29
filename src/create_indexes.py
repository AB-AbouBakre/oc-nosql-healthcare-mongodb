import os
from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI manquant dans .env")

client = MongoClient(MONGO_URI)
db = client[os.getenv("MONGO_DATABASE", "medical_db")]
collection = db["patients"]

print("🔧 Création des index pour optimiser les requêtes...\n")

# 1. Index sur Hospital (filtres fréquents)
collection.create_index([("Hospital", ASCENDING)], name="idx_hospital")
print("✓ Index créé : Hospital")

# 2. Index sur Medical Condition (statistiques par pathologie)
collection.create_index([("Medical Condition", ASCENDING)], name="idx_medical_condition")
print("✓ Index créé : Medical Condition")

# 3. Index sur Date of Admission (tri chronologique, dashboards)
collection.create_index([("Date of Admission", DESCENDING)], name="idx_date_admission")
print("✓ Index créé : Date of Admission (décroissant)")

# 4. Index sur Doctor (filtres par médecin)
collection.create_index([("Doctor", ASCENDING)], name="idx_doctor")
print("✓ Index créé : Doctor")

# 5. Index sur Insurance Provider (analyses financières)
collection.create_index([("Insurance Provider", ASCENDING)], name="idx_insurance_provider")
print("✓ Index créé : Insurance Provider")

# 6. Index sur Admission Type (Emergency/Urgent/Elective)
collection.create_index([("Admission Type", ASCENDING)], name="idx_admission_type")
print("✓ Index créé : Admission Type")

# 7. Index composé Hospital + Date (requêtes combinées fréquentes)
collection.create_index([
    ("Hospital", ASCENDING),
    ("Date of Admission", DESCENDING)
], name="idx_hospital_date")
print("✓ Index composé créé : Hospital + Date of Admission")

# 8. Index composé Medical Condition + Date (évolution temporelle)
collection.create_index([
    ("Medical Condition", ASCENDING),
    ("Date of Admission", DESCENDING)
], name="idx_condition_date")
print("✓ Index composé créé : Medical Condition + Date of Admission")

# 9. Index texte sur Name (recherche patients)
collection.create_index([("Name", TEXT)], name="idx_name_text")
print("✓ Index texte créé : Name")

# Afficher tous les index
print("\n📊 Index existants dans la collection 'patients' :")
for idx in collection.list_indexes():
    print(f"  • {idx['name']}: {idx['key']}")

# Statistiques
stats = collection.index_information()
print(f"\n✅ Total : {len(stats)} index créés (incluant l'index _id par défaut)")

client.close()
print("\n🎯 Création des index terminée avec succès !")