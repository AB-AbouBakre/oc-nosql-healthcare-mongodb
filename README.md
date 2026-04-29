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

## Sécurité des credentials

Les identifiants et mots de passe ne sont **pas stockés en clair** dans le code. La configuration utilise un fichier `.env` local qui est exclu du versionnement.

### Configuration

1. Créer un fichier `.env` à la racine du projet en se basant sur `.env.example` :

```bash
cp .env.example .env
```

2. Remplir les valeurs réelles dans `.env` :

```env
MONGO_ROOT_USERNAME=votre_username
MONGO_ROOT_PASSWORD=votre_password
MONGO_DATABASE=medical_db
MONGO_URI=mongodb://votre_username:votre_password@mongo:27017/medical_db?authSource=admin
MONGO_URI_LOCAL=mongodb://votre_username:votre_password@localhost:27017/medical_db?authSource=admin
CSV_PATH=data/healthcare_dataset.csv
```

3. Le fichier `.env` est automatiquement ignoré par Git (voir `.gitignore`)

### Utilisation des variables d'environnement

- **Dans Docker** : les variables sont chargées via `env_file` dans `docker-compose.yml`
- **En local** : les scripts Python utilisent `python-dotenv` pour charger `.env`

**Fichiers concernés** :
- `docker-compose.yml` : substitution de variables `${VARIABLE}`
- `src/migrate.py` : `load_dotenv()` + `os.getenv()`
- `tests/check_db.py` : `load_dotenv()` + `os.getenv()`
- `tests/data_quality.py` : `load_dotenv()` + `os.getenv()`
## Structure du projet

## Structure du projet

```text
oc-nosql-medical/
├── data/
│   └── healthcare_dataset.csv      # Fichier CSV contenant les données médicales
├── src/
│   ├── migrate.py                  # Script principal de migration CSV → MongoDB
│   └── create_indexes.py           # Script de création automatique des index
├── tests/
│   ├── check_db.py                 # Script de vérification rapide (compte / exemple)
│   ├── data_quality.py             # Script de contrôle qualité (count, NA, types, doublons)
│   └── test_indexes.py             # Script de test des performances des index
├── init-mongo/
│   └── init-users.js               # Création automatique de app_user et analyst_user
├── requirements.txt                # Dépendances Python (pymongo, pandas, python-dotenv)
├── Dockerfile                      # Image Docker pour la migration
├── docker-compose.yml              # Orchestration MongoDB + migration
├── .env.example                    # Template pour les variables d'environnement
├── .gitignore                      # Exclusion de .env et fichiers sensibles
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

### 3. Configurer les variables d'environnement

Créer le fichier `.env` à partir du template :

```bash
cp .env.example .env
```

Éditer `.env` et remplir les valeurs réelles (voir section [Sécurité des credentials](#sécurité-des-credentials)).

### 4. Lancer MongoDB et la migration

```bash
docker compose up --build
```

Cette commande :

- démarre le service **`medical-mongo`** (MongoDB) avec la base `medical_db`, en créant un utilisateur root depuis les variables d'environnement `.env` ;
- monte le script `init-mongo/init-users.js` dans `/docker-entrypoint-initdb.d`, qui crée automatiquement :
  - `app_user` (rôle `readWrite` sur `medical_db`) ;
  - `analyst_user` (rôle `read` sur `medical_db`) ;
- démarre le service **`medical-migration`**, qui :
  - exécute `src/migrate.py` pour charger les données CSV dans MongoDB ;
  - exécute `src/create_indexes.py` pour créer les 9 index d'optimisation ;
  - affiche dans les logs :

    ```text
    Lecture du CSV...
    55500 lignes à insérer.
    55500 documents insérés.
    
    🔧 Création des index pour optimiser les requêtes...
    ✓ Index créé : Hospital
    ✓ Index créé : Medical Condition
    ...
    ✅ Total : 10 index créés (incluant l'index _id par défaut)
    🎯 Création des index terminée avec succès !
    ```

  - se termine une fois la migration et l'indexation terminées (code de sortie 0).

### 5. Arrêter les services

```bash
docker compose down -v
```

Cela arrête les conteneurs et supprime les volumes si nécessaire.

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

## Optimisation des performances : Index MongoDB

Pour améliorer les temps de réponse des requêtes, **9 index** ont été créés automatiquement sur la collection `patients`.

### Index créés

#### Index simples (6)

| Champ | Usage | Performance |
|-------|-------|-------------|
| `Hospital` | Filtres par établissement | 3ms pour 7 résultats |
| `Medical Condition` | Statistiques par pathologie | 15ms pour 9k résultats |
| `Date of Admission` | Tri chronologique | 1ms pour les 10 plus récents |
| `Doctor` | Filtres par médecin | Optimisé |
| `Insurance Provider` | Analyses financières | Optimisé |
| `Admission Type` | Emergency/Urgent/Elective | 25ms pour 18k résultats |

#### Index composés (2)

- **Hospital + Date of Admission** : Patients récents d'un hôpital (0ms, optimal pour dashboards temps réel)
- **Medical Condition + Date** : Évolution temporelle d'une pathologie

#### Index texte (1)

- **Name** : Recherche full-text de patients par nom

### Résultats des tests de performance

Avec **55 500 documents** dans la collection :
- ✅ Toutes les requêtes utilisent les index (stratégie `IXSCAN`/`FETCH`)
- ✅ Temps de réponse **< 25ms** pour toutes les requêtes testées
- ✅ Aucun scan complet de collection (`COLLSCAN` évité)

### Création automatique des index

Les index sont créés automatiquement lors du lancement de `docker compose up` via le script `src/create_indexes.py` qui s'exécute après la migration.

### Vérification manuelle

```bash
# Tester les performances des index
python tests/test_indexes.py

# Ou se connecter à MongoDB directement
docker exec -it medical-mongo mongosh -u root-oc -p <votre_password> --authenticationDatabase admin
use medical_db
db.patients.getIndexes()
db.patients.find({"Hospital": "Sons and Miller"}).explain("executionStats")
```

**Note** : Le script `tests/test_indexes.py` utilise `EXPLAIN` pour vérifier que les index sont bien utilisés et mesurer les temps de réponse.

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

## Pistes d'industrialisation

Pour aller plus loin :

- **Sécurité renforcée** :
  - Rotation automatique des mots de passe via un gestionnaire de secrets (Vault, AWS Secrets Manager) ;
  - Chiffrement des données au repos et en transit (TLS/SSL) ;
  - Audit des accès MongoDB avec des logs détaillés ;
  
- **Optimisation des index** :
  - Analyser les requêtes réelles via MongoDB Profiler ou Atlas Performance Advisor ;
  - Créer des index partiels ou sparse pour économiser l'espace disque ;
  - Monitorer l'utilisation des index avec `db.collection.aggregate([{$indexStats:{}}])` ;

- **Tests automatisés** : 
  - Intégrer `tests/data_quality.py` et `tests/test_indexes.py` dans une pipeline CI ;
  - Ajouter des tests plus fins (contraintes métier, distributions, etc.) ;
  - Tests de charge pour valider les performances sous charge ;

- **Docker Compose avancé** : 
  - Ajouter un service dédié pour les tests ;
  - Utiliser Docker secrets pour les credentials en production ;

- **Déploiement cloud** :
  - Stockage du CSV sur un bucket (Amazon S3, Google Cloud Storage) ;
  - Base NoSQL managée (MongoDB Atlas, Amazon DocumentDB) ;
  - Exécution du conteneur de migration sur un orchestrateur (ECS, Kubernetes) ;
  - Gestion des secrets via un service dédié (AWS Secrets Manager, Vault, etc.) ;
  
- **Monitoring et observabilité** :
  - Intégration avec Prometheus/Grafana pour surveiller MongoDB ;
  - Alertes automatiques sur les performances des index ;
  - Logs centralisés (ELK Stack, CloudWatch).