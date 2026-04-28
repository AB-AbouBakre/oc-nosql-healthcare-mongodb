import os
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv

# Charger les variables depuis le fichier .env
load_dotenv()

CSV_PATH = os.getenv("CSV_PATH", "data/healthcare_dataset.csv")

# URI depuis les variables d'environnement
MONGO_URI = os.getenv("MONGO_URI_LOCAL")
if not MONGO_URI:
    raise ValueError("❌ MONGO_URI_LOCAL manquant dans .env")

DB_NAME = os.getenv("MONGO_DATABASE", "medical_db")
COLLECTION_NAME = "patients"


def check_missing_values(df: pd.DataFrame) -> None:
    missing = df.isna().sum()
    total_rows = len(df)
    print("\n[CHECK] Valeurs manquantes par colonne (nb et pourcentage) :")
    any_missing = False
    for col, nb in missing.items():
        if nb > 0:
            any_missing = True
            pct = nb * 100.0 / total_rows
            print(f"  - {col}: {nb} valeurs manquantes ({pct:.2f} %)")
    if not any_missing:
        print("[CHECK] Aucune valeur manquante détectée.")


def check_basic_types(df: pd.DataFrame) -> None:
    print("\n[CHECK] Types de colonnes inférés par pandas :")
    print(df.dtypes)


def check_duplicates(df: pd.DataFrame, subset_cols=None) -> None:
    if subset_cols is None:
        subset_cols = ["Name", "Date of Admission", "Hospital"]

    for col in subset_cols:
        if col not in df.columns:
            print(f"[CHECK] Colonne '{col}' absente, impossible de vérifier les doublons dessus.")
            return

    duplicated = df.duplicated(subset=subset_cols)
    nb_dups = duplicated.sum()
    if nb_dups > 0:
        print(f"\n[CHECK] ATTENTION : {nb_dups} doublons détectés sur les colonnes {subset_cols}.")
        print(df[duplicated].head())
    else:
        print(f"\n[CHECK] Aucun doublon détecté sur les colonnes {subset_cols}.")


def compare_csv_vs_mongo() -> None:
    print("\n[CHECK] Comparaison CSV vs MongoDB")

    # Lecture CSV
    df = pd.read_csv(CSV_PATH)
    nb_csv = len(df)
    print(f"- Nombre de lignes dans le CSV : {nb_csv}")

    # Connexion MongoDB
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    nb_mongo = collection.count_documents({})
    print(f"- Nombre de documents dans MongoDB : {nb_mongo}")

    if nb_csv == nb_mongo:
        print("[CHECK] OK : même nombre de lignes dans le CSV et de documents dans MongoDB.")
    else:
        print("[CHECK] ATTENTION : différence entre CSV et MongoDB.")

    client.close()

    # Checks sur le DataFrame
    check_missing_values(df)
    check_basic_types(df)
    check_duplicates(df)


if __name__ == "__main__":
    compare_csv_vs_mongo()