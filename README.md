# Migration de données médicales vers MongoDB

Ce projet met en place une pipeline de migration de données à partir d’un fichier CSV (`healthcare_dataset.csv`) vers une base de données **MongoDB** dockerisée.  
L’objectif est de charger un jeu de données médicales (55 500 lignes) dans MongoDB, de vérifier la qualité des données et de préparer une architecture simple et reproductible avec **Docker**.

## Table des matières

- [Contexte](#contexte)
- [Architecture technique](#architecture-technique)
- [Prérequis](#prérequis)
- [Structure du projet](#structure-du-projet)
- [Lancer la migration avec Docker](#lancer-la-migration-avec-docker)
- [Vérification et qualité des données](#vérification-et-qualité-des-données)
- [Schéma MongoDB et authentification](#schéma-mongodb-et-authentification)
- [Pistes d’industrialisation](#pistes-dindustrialisation)

## Contexte

Ce projet s’inscrit dans la mission **« Migrez des données médicales à l’aide du NoSQL »**.  
À partir d’un fichier CSV contenant des informations sur des patients (nom, âge, type de sang, dates d’admission et de sortie, médecin, hôpital, etc.), il s’agit de :

- migrer les données vers une base **MongoDB** ;
- vérifier que la migration est complète et cohérente ;
- mettre en place une authentification basique au niveau de la base ;
- documenter l’architecture pour une future industrialisation.

## Architecture technique

L’architecture repose sur :

- un fichier **CSV** source dans le répertoire `data/` (par ex. `data/healthcare_dataset.csv`) ;
- un script Python de **migration** : `src/migrate.py`, qui :
  - lit le CSV avec `pandas` ;
  - se connecte à MongoDB avec `pymongo` ;
  - insère les 55 500 lignes dans une collection MongoDB (par ex. `patients`) ;
- un script Python de **contrôle qualité** : `tests/data_quality.py`, qui compare le CSV et la base MongoDB et analyse la qualité des données ;
- un script de **vérification rapide** : `tests/check_db.py`, qui affiche le nombre de documents et un exemple de document ;
- un fichier **`Dockerfile`** pour construire l’image du conteneur de migration ;
- un fichier **`docker-compose.yml`** qui orchestre 2 services :
  - `medical-mongo` : base MongoDB (image officielle `mongo:6.0`), avec un utilisateur administrateur ;
  - `medical-migration` : conteneur Python qui exécute `src/migrate.py`.

Les services communiquent via un réseau Docker nommé `medical-net`, et les données MongoDB sont stockées dans un volume `mongo_data`.

## Prérequis

Pour exécuter ce projet :

- **Docker Desktop** installé et démarré ;
- **Git** pour cloner le dépôt ;
- **Python 3.x** pour exécuter les scripts locaux (`tests/data_quality.py`, `tests/check_db.py`) si nécessaire ;
- Les dépendances Python (`pandas`, `pymongo`, …) installées via `pip install -r requirements.txt` si vous exécutez les scripts hors Docker.

## Structure du projet

```text
oc-nosql-medical/
├── data/
│   └── healthcare_dataset.csv      # Fichier CSV contenant les données médicales
├── src/
│   └── migrate.py                  # Script principal de migration CSV → MongoDB
├── tests/
│   ├── check_db.py                 # Script de vérification rapide (compte / exemple)
│   └── data_quality.py             # Script de contrôle qualité (count, NA, types, doublons)
├── init-mongo/
│   └── init-users.js               # Création automatique de app_user et analyst_user
├── requirements.txt                # Dépendances Python (pymongo, pandas, …)
├── Dockerfile                      # Image Docker pour la migration
├── docker-compose.yml              # Orchestration MongoDB + migration
├── docs/
│   └── schema.md                   # Schéma de la base MongoDB (structure des documents)
└── README.md                       # Ce fichier
```

## Lancer la migration avec Docker

### 1. Cloner le dépôt

```bash
git clone https://github.com/AB-AbouBakre/oc-nosql-healthcare-mongodb.git
cd oc-nosql-healthcare-mongodb
```

### 2. Vérifier la présence du fichier CSV

Assurez-vous que le fichier suivant existe :

```text
data/healthcare_dataset.csv
```

### 3. Lancer MongoDB et la migration

```bash
docker compose up --build
```

Cette commande :

- démarre le service **`medical-mongo`** (MongoDB) avec la base `medical_db`, en créant un utilisateur root `root-oc` avec un mot de passe fort ;
- monte le script `init-mongo/init-users.js` dans `/docker-entrypoint-initdb.d`, qui crée automatiquement :
  - `app_user` (rôle `readWrite` sur `medical_db`) ;
  - `analyst_user` (rôle `read` sur `medical_db`) ;
- démarre le service **`medical-migration`**, qui :
  - lit le CSV,
  - affiche dans les logs :

    ```text
    Lecture du CSV...
    55500 lignes à insérer.
    55500 documents insérés.
    ```

  - se termine une fois la migration terminée (code de sortie 0).

### 4. Arrêter les services

```bash
docker compose down -v
```

Cela arrête les conteneurs et supprime les volumes si nécessaire.

## Vérification et qualité des données

### Vérification rapide du contenu MongoDB

Le script `tests/check_db.py` permet de vérifier rapidement l’état de la collection :

```bash
python tests/check_db.py
```

Ce script :

- se connecte à `medical_db.patients` via `pymongo` ;
- affiche le nombre total de documents ;
- affiche un exemple de document.

Exemple de sortie :

```text
Nombre de documents : 55500
Exemple de document :
{ "_id": ObjectId("..."), "Name": "...", "Age": 30, ... }
```

### Contrôles de qualité des données

Le script `tests/data_quality.py` réalise des contrôles de qualité :

```bash
python tests/data_quality.py
```

Il :

- compare le **nombre de lignes dans le CSV** et le **nombre de documents dans MongoDB** (55 500 vs 55 500) ;
- affiche le résumé des **valeurs manquantes** par colonne (aucune valeur manquante détectée dans ce dataset) ;
- affiche les **types de colonnes** inférés par `pandas` (entiers, flottants, chaînes, etc.) ;
- détecte les **doublons potentiels** sur les colonnes `Name`, `Date of Admission`, `Hospital` (environ 5 500 lignes, soit ~10 %, correspondant possiblement à des réadmissions ou enregistrements multiples).

Ces contrôles permettent de documenter la qualité de la migration et les éventuelles limites (présence de doublons métier).

## Schéma MongoDB et authentification

### Schéma de la base

- Base : `medical_db`  
- Collection : `patients`  
- Un document par ligne du CSV `healthcare_dataset.csv`.

Les champs correspondent aux colonnes du CSV. Exemple de document :

```json
{
  "_id": "ObjectId(...)",
  "Name": "Bobby JacksOn",
  "Age": 30,
  "Gender": "Male",
  "Blood Type": "B-",
  "Medical Condition": "Cancer",
  "Date of Admission": "2024-01-31",
  "Doctor": "Matthew Smith",
  "Hospital": "Sons and Miller",
  "Insurance Provider": "Blue Cross",
  "Billing Amount": 18856.28,
  "Room Number": 328,
  "Admission Type": "Urgent",
  "Discharge Date": "2024-02-02",
  "Medication": "Paracetamol",
  "Test Results": "Normal"
}
```

Types principaux :

- chaînes : `Name`, `Gender`, `Blood Type`, `Medical Condition`, `Doctor`, `Hospital`, `Insurance Provider`, `Admission Type`, `Medication`, `Test Results` ;
- entiers : `Age`, `Room Number` ;
- flottant : `Billing Amount` ;
- chaînes (format `YYYY-MM-DD`) : `Date of Admission`, `Discharge Date`.

### Authentification et rôles

MongoDB n’est pas accessible en anonyme. Dans ce projet :

- un utilisateur root `root-oc` est créé via les variables d’environnement `MONGO_INITDB_ROOT_USERNAME` et `MONGO_INITDB_ROOT_PASSWORD` ;
- deux utilisateurs applicatifs sont créés automatiquement par `init-mongo/init-users.js` :

  - `app_user` : rôle `readWrite` sur `medical_db` (compte applicatif) ;
  - `analyst_user` : rôle `read` sur `medical_db` (compte analyste).

Exemples d’URI de connexion :

```text
# Administrateur
mongodb://root-oc:<mot_de_passe_root>@localhost:27017/medical_db?authSource=admin

# Compte applicatif
mongodb://app_user:<mot_de_passe_app>@localhost:27017/medical_db?authSource=medical_db

# Compte analyste
mongodb://analyst_user:<mot_de_passe_analyst>@localhost:27017/medical_db?authSource=medical_db
```

En production, on applique le principe de moindre privilège :

- **Administrateur (DBA)** : gestion complète de la base (création d’utilisateurs, index, sauvegardes/restaurations).  
- **Compte applicatif** : `readWrite` limité aux collections nécessaires (par ex. `medical_db.patients`).  
- **Compte analyste** : `read` uniquement sur certaines collections (analyses et reporting).

## Pistes d’industrialisation

Pour aller plus loin :

- **Tests automatisés** : intégrer `tests/data_quality.py` dans une pipeline CI, ajouter des tests plus fins (contraintes métier, distributions, etc.) ;
- **Docker Compose avancé** : ajouter un service dédié pour les tests, gérer les variables sensibles via un fichier `.env` non versionné ;
- **Déploiement cloud** :
  - stockage du CSV sur un bucket (par ex. Amazon S3) ;
  - base NoSQL managée (MongoDB Atlas, Amazon DocumentDB) ;
  - exécution du conteneur de migration sur un orchestrateur (ECS, Kubernetes) ;
  - gestion des secrets via un service dédié (AWS Secrets Manager, Vault, etc.).