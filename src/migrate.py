import os
import pandas as pd
from pymongo import MongoClient

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://root:rootpassword@localhost:27017/medical_db?authSource=admin"
)

CSV_PATH = os.getenv(
    "CSV_PATH",
    "data/healthcare_dataset.csv"
)

client = MongoClient(MONGO_URI)
db = client["medical_db"]
collection = db["patients"]

print("Lecture du CSV...")
df = pd.read_csv(CSV_PATH)

# Nettoyage simple : remplacer NaN par None pour MongoDB
df = df.where(pd.notna(df), None)

# (optionnel) typer quelques colonnes selon ton CSV Kaggle
# df["Age"] = df["Age"].astype("Int64")
# df["Diabetes"] = df["Diabetes"].astype(bool)

records = df.to_dict(orient="records")
print(f"{len(records)} lignes à insérer.")

# On peut vider la collection avant (full reload)
collection.delete_many({})

result = collection.insert_many(records)
print(f"{len(result.inserted_ids)} documents insérés.")

client.close()

