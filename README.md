# Migration de données médicales vers MongoDB

Ce projet implémente une pipeline de migration de données à partir d'un fichier CSV (`healthcare_dataset.csv`) vers une base de données MongoDB. Les données sont chargées via un script Python et insérées dans une collection MongoDB, hébergée dans un conteneur Docker. Un script de vérification permet de contrôler le nombre de documents migrés et d’inspecter un exemple de document.

## Table des matières

- [Prérequis](#prérequis)
- [Structure du projet](#structure-du-projet)
- [Installation](#installation)
- [Exécution de la migration](#exécution-de-la-migration)
- [Vérification des données](#vérification-des-données)
- [Schéma MongoDB et authentification](#schéma-mongodb-et-authentification)
- [Pistes d’évolution (tests, Docker Compose, AWS)](#pistes-dévolution-tests-docker-compose-aws)

## Prérequis

Pour exécuter ce projet localement, il est nécessaire d’avoir installé :

- **Python 3.x**
- **Docker** (pour exécuter MongoDB dans un conteneur)
- **Git** (pour cloner le dépôt)

Les dépendances Python spécifiques (pandas, pymongo, etc.) sont listées dans `requirements.txt`.

## Structure du projet

```text
oc-nosql-medical/
├── .venv/                     # Environnement virtuel Python (non versionné)
├── data/
│   └── healthcare_dataset.csv # Fichier CSV contenant les données médicales
├── src/
│   └── migrate.py             # Script principal de migration CSV → MongoDB
├── tests/
│   └── check_db.py            # Script de vérification du contenu MongoDB
├── requirements.txt           # Dépendances Python (pymongo, pandas, …)
├── Dockerfile                 # (à ajouter) Image pour exécuter la migration en conteneur
├── docker-compose.yml         # (à ajouter) Orchestration MongoDB + migration
└── README.md                  # Ce fichier
```

*(Les fichiers `Dockerfile` et `docker-compose.yml` seront ajoutés dans une étape ultérieure du projet.)*

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/AB-AbouBakre/oc-nosql-healthcare-mongodb.git
cd oc-nosql-healthcare-mongodb
```

### 2. Créer et activer l’environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate  # macOS / Linux
pip install -r requirements.txt
```

### 3. Vérifier la présence du fichier CSV

Assurez-vous que le fichier suivant existe :

```text
data/healthcare_dataset.csv
```

Ce fichier contient les données médicales à migrer (par exemple des informations patients, mesures, diagnostics, etc.).

## Exécution de la migration

### 1. Démarrer MongoDB dans Docker

Lancer une instance MongoDB accessible depuis la machine hôte :

```bash
docker run -d --name medical-mongo -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=root \
  -e MONGO_INITDB_ROOT_PASSWORD=rootpassword \
  mongo:6.0
```

Cette commande démarre un conteneur MongoDB sur le port `27017`, avec un utilisateur administrateur `root` / `rootpassword`.

### 2. Lancer le script de migration

Depuis la racine du projet, avec l’environnement virtuel activé :

```bash
export MONGO_URI="mongodb://root:rootpassword@localhost:27017/medical_db?authSource=admin"
python src/migrate.py
```

Le script `migrate.py` :

- lit le fichier `data/healthcare_dataset.csv` avec `pandas`,
- remplace les valeurs manquantes (`NaN`) par `None` pour compatibilité MongoDB,
- se connecte à la base `medical_db` de MongoDB,
- insère toutes les lignes du CSV dans la collection `patients`,
- affiche dans la console le nombre de lignes lues et de documents insérés,
- effectue un comptage final des documents dans la collection.

Exemple de sortie :

```text
Lecture du CSV...
55500 lignes à insérer.
55500 documents insérés.
Nombre de documents dans la collection : 55500
```

*(les valeurs exactes dépendent du dataset)*

## Vérification des données

Un script de vérification simple est fourni dans `tests/check_db.py` :

```bash
python tests/check_db.py
```

Ce script :

- se connecte à `medical_db.patients` via `pymongo`,
- affiche le nombre total de documents présents dans la collection,
- affiche un exemple de document pour contrôle visuel.

Exemple de sortie :

```text
Nombre de documents : 55500
Exemple de document :
{'_id': ObjectId('...'), 'Name': 'Bobby JacksOn', 'Age': 30, 'Gender': 'Male', 'Blood Type': 'B-', 'Medical Condition': 'Cancer', 'Date of Admission': '2024-01-31', 'Doctor': 'Matthew Smith', 'Hospital': 'Sons and Miller', 'Insurance Provider': 'Blue Cross', 'Billing Amount': 18856.281305978155, 'Room Number': 328, 'Admission Type': 'Urgent', 'Discharge Date': '2024-02-02', 'Medication': 'Paracetamol', 'Test Results': 'Normal'}
```

Ce script permet de valider rapidement que la migration a abouti.

### Tests d'intégrité des données

Le script `tests/data_quality.py` permet de réaliser des vérifications simples sur la qualité des données :

- comparaison du nombre de lignes dans le CSV et du nombre de documents dans MongoDB,
- résumé des valeurs manquantes par colonne,
- affichage des types de colonnes inférés par pandas,
- détection de doublons sur les colonnes `Name`, `Date of Admission`, `Hospital`.

Exécution :

```bash
python tests/data_quality.py
```
## Schéma MongoDB et authentification

### Schéma de la base

- Base de données : `medical_db`
- Collection : `patients`
- Un document par ligne du CSV `healthcare_dataset.csv`.

Les champs correspondent directement aux colonnes du fichier CSV. Un document typique ressemble à :

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
  "Billing Amount": 18856.281305978155,
  "Room Number": 328,
  "Admission Type": "Urgent",
  "Discharge Date": "2024-02-02",
  "Medication": "Paracetamol",
  "Test Results": "Normal"
}
```

Types principaux utilisés par MongoDB dans cette première version :

- `Name`, `Gender`, `Blood Type`, `Medical Condition`, `Doctor`, `Hospital`, `Insurance Provider`, `Admission Type`, `Medication`, `Test Results` : chaînes de caractères,
- `Age`, `Room Number` : entiers,
- `Billing Amount` : nombre à virgule flottante,
- `Date of Admission`, `Discharge Date` : actuellement stockées comme chaînes de caractères (format `YYYY-MM-DD`) telles que fournies dans le CSV.

Dans une itération ultérieure, ces champs de date pourront être convertis en véritables types `Date` MongoDB, et des champs dérivés (par exemple durée de séjour) pourront être ajoutés.

### Index (pistes)

À partir de ce modèle, des index pertinents pourraient être :

- index sur `Medical Condition` (analyses par pathologie),
- index sur `Doctor` ou `Hospital` (analyse d’activité),
- index sur une future clé patient si un champ d’identifiant unique est ajouté.

Ces index peuvent être créés dans une étape ultérieure, une fois les besoins de requêtage clarifiés.

### Authentification et rôles

Dans la configuration actuelle :

- l’utilisateur `root` (défini via les variables d’environnement Docker) dispose de droits administrateur,
- la connexion se fait via l’URI :

```text
mongodb://root:rootpassword@localhost:27017/medical_db?authSource=admin
```

Pour un environnement plus sécurisé, il est possible d’ajouter un utilisateur applicatif dédié avec un rôle `readWrite` limité à `medical_db` :

```js
db.createUser({
  user: "app_user",
  pwd: "app_password",
  roles: [
    { role: "readWrite", db: "medical_db" }
  ]
});
```

*(Cette création d’utilisateur pourra être automatisée avec un script d’init Docker dans la suite du projet.)*

## Pistes d’évolution (tests, Docker Compose, AWS)

Les améliorations suivantes sont prévues dans les étapes suivantes du projet :

- **Tests automatisés** :
  - scripts Python supplémentaires pour vérifier l’intégrité des données avant/après migration (types, doublons, valeurs manquantes),
  - éventuelle intégration de `pytest` pour des tests plus complets.

- **Docker Compose** :
  - ajout d’un `docker-compose.yml` pour lancer automatiquement la base MongoDB et le conteneur de migration dans un même réseau Docker,
  - utilisation de volumes pour persister les données MongoDB et monter le fichier CSV.

- **Étude du déploiement sur AWS** :
  - documentation des options de déploiement sur AWS (S3 pour le stockage des CSV et des sauvegardes, Amazon DocumentDB compatible MongoDB, déploiement de conteneurs sur ECS, etc.),
  - cette étude sera fournie dans un document séparé (`docs/aws_research.md`) et servira de support à la présentation finale.
