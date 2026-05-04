"""
Script de migration de données médicales depuis un fichier CSV vers MongoDB.

Ce script lit un fichier CSV contenant des données de patients, nettoie les données,
et les insère dans une collection MongoDB. Il utilise des variables d'environnement
pour la configuration et est découpé en fonctions modulaires.

Auteur: Abdellah ABOU BAKRE
Date: 2026-05-04
"""

import os
import pandas as pd
from pymongo import MongoClient
from dotenv import load_dotenv


def load_environment_variables():
    """
    Charge les variables d'environnement depuis le fichier .env.
    
    Returns:
        tuple: (MONGO_URI, CSV_PATH, DATABASE_NAME)
    
    Raises:
        ValueError: Si MONGO_URI est manquant dans .env
    """
    # Charger le fichier .env
    load_dotenv()
    
    # Récupérer l'URI MongoDB (obligatoire)
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("❌ MONGO_URI manquant dans le fichier .env")
    
    # Récupérer le chemin du CSV (avec valeur par défaut)
    csv_path = os.getenv("CSV_PATH", "data/healthcare_dataset.csv")
    
    # Récupérer le nom de la base de données (avec valeur par défaut)
    database_name = os.getenv("MONGO_DATABASE", "medical_db")
    
    return mongo_uri, csv_path, database_name


def connect_to_mongodb(mongo_uri, database_name):
    """
    Établit une connexion à MongoDB et retourne la base de données.
    
    Args:
        mongo_uri (str): URI de connexion MongoDB
        database_name (str): Nom de la base de données
    
    Returns:
        tuple: (client, database, collection)
    """
    print("🔌 Connexion à MongoDB...")
    
    # Créer le client MongoDB
    client = MongoClient(mongo_uri)
    
    # Sélectionner la base de données
    database = client[database_name]
    
    # Sélectionner la collection "patients"
    collection = database["patients"]
    
    print(f"✅ Connecté à la base '{database_name}', collection 'patients'")
    
    return client, database, collection


def read_csv_file(csv_path):
    """
    Lit le fichier CSV et retourne un DataFrame pandas.
    
    Args:
        csv_path (str): Chemin vers le fichier CSV
    
    Returns:
        pd.DataFrame: DataFrame contenant les données du CSV
    
    Raises:
        FileNotFoundError: Si le fichier CSV n'existe pas
    """
    print(f"📖 Lecture du fichier CSV : {csv_path}")
    
    # Vérifier que le fichier existe
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"❌ Fichier CSV introuvable : {csv_path}")
    
    # Lire le CSV avec pandas
    dataframe = pd.read_csv(csv_path)
    
    print(f"✅ {len(dataframe)} lignes lues depuis le CSV")
    
    return dataframe


def clean_data(dataframe):
    """
    Nettoie les données du DataFrame avant insertion dans MongoDB.
    
    Opérations effectuées :
    - Remplacement des valeurs NaN par None (compatible MongoDB)
    - Conversion optionnelle de types de colonnes
    
    Args:
        dataframe (pd.DataFrame): DataFrame à nettoyer
    
    Returns:
        pd.DataFrame: DataFrame nettoyé
    """
    print("🧹 Nettoyage des données...")
    
    # Remplacer les NaN par None (null en MongoDB)
    # MongoDB ne supporte pas NaN, il faut utiliser None
    cleaned_df = dataframe.where(pd.notna(dataframe), None)
    
    # Conversion optionnelle de types (à adapter selon votre CSV)
    # Exemple : forcer Age en entier si nécessaire
    # if "Age" in cleaned_df.columns:
    #     cleaned_df["Age"] = cleaned_df["Age"].astype("Int64")
    
    # Exemple : convertir une colonne booléenne
    # if "Diabetes" in cleaned_df.columns:
    #     cleaned_df["Diabetes"] = cleaned_df["Diabetes"].astype(bool)
    
    print("✅ Données nettoyées")
    
    return cleaned_df


def clear_collection(collection):
    """
    Vide complètement la collection MongoDB avant insertion.
    
    Permet un full reload : supprime tous les documents existants
    pour éviter les doublons lors d'une nouvelle migration.
    
    Args:
        collection: Collection MongoDB
    """
    print("🗑️  Suppression des documents existants...")
    
    # Compter les documents avant suppression
    count_before = collection.count_documents({})
    
    # Supprimer tous les documents
    result = collection.delete_many({})
    
    print(f"✅ {result.deleted_count} documents supprimés (total avant : {count_before})")


def insert_data_to_mongodb(collection, dataframe):
    """
    Insère les données du DataFrame dans la collection MongoDB.
    
    Args:
        collection: Collection MongoDB
        dataframe (pd.DataFrame): DataFrame contenant les données à insérer
    
    Returns:
        int: Nombre de documents insérés
    """
    print("📥 Insertion des documents dans MongoDB...")
    
    # Convertir le DataFrame en liste de dictionnaires
    # orient="records" crée une liste de dicts (un dict par ligne)
    records = dataframe.to_dict(orient="records")
    
    print(f"📊 {len(records)} documents à insérer...")
    
    # Insertion en masse (bulk insert) pour de meilleures performances
    result = collection.insert_many(records)
    
    # Nombre de documents insérés
    inserted_count = len(result.inserted_ids)
    
    print(f"✅ {inserted_count} documents insérés avec succès")
    
    return inserted_count


def verify_insertion(collection, expected_count):
    """
    Vérifie que le nombre de documents insérés correspond au nombre attendu.
    
    Args:
        collection: Collection MongoDB
        expected_count (int): Nombre de documents attendus
    
    Raises:
        AssertionError: Si le nombre de documents ne correspond pas
    """
    print("🔍 Vérification de l'insertion...")
    
    # Compter les documents dans la collection
    actual_count = collection.count_documents({})
    
    print(f"📊 Documents dans la collection : {actual_count}")
    print(f"📊 Documents attendus : {expected_count}")
    
    # Vérifier la cohérence
    if actual_count == expected_count:
        print("✅ Vérification réussie : nombre de documents correct")
    else:
        raise AssertionError(
            f"❌ Erreur : {actual_count} documents trouvés, {expected_count} attendus"
        )


def close_connection(client):
    """
    Ferme la connexion au client MongoDB.
    
    Args:
        client: Client MongoDB
    """
    print("🔌 Fermeture de la connexion MongoDB...")
    client.close()
    print("✅ Connexion fermée")


def main():
    """
    Fonction principale qui orchestre la migration complète.
    
    Étapes :
    1. Chargement des variables d'environnement
    2. Connexion à MongoDB
    3. Lecture du fichier CSV
    4. Nettoyage des données
    5. Suppression des documents existants
    6. Insertion des nouvelles données
    7. Vérification de l'insertion
    8. Fermeture de la connexion
    """
    print("=" * 60)
    print("🚀 DÉMARRAGE DE LA MIGRATION DE DONNÉES MÉDICALES")
    print("=" * 60)
    
    try:
        # Étape 1 : Charger les variables d'environnement
        mongo_uri, csv_path, database_name = load_environment_variables()
        
        # Étape 2 : Connexion à MongoDB
        client, database, collection = connect_to_mongodb(mongo_uri, database_name)
        
        # Étape 3 : Lecture du CSV
        dataframe = read_csv_file(csv_path)
        
        # Étape 4 : Nettoyage des données
        cleaned_dataframe = clean_data(dataframe)
        
        # Étape 5 : Suppression des documents existants (full reload)
        clear_collection(collection)
        
        # Étape 6 : Insertion des données
        inserted_count = insert_data_to_mongodb(collection, cleaned_dataframe)
        
        # Étape 7 : Vérification
        verify_insertion(collection, expected_count=len(cleaned_dataframe))
        
        # Étape 8 : Fermeture de la connexion
        close_connection(client)
        
        print("=" * 60)
        print("✅ MIGRATION TERMINÉE AVEC SUCCÈS")
        print(f"📊 Total : {inserted_count} documents migrés")
        print("=" * 60)
    
    except Exception as error:
        print("=" * 60)
        print(f"❌ ERREUR LORS DE LA MIGRATION : {error}")
        print("=" * 60)
        raise


# Point d'entrée du script
if __name__ == "__main__":
    main()