# Schéma de la base MongoDB `medical_db`

## 1. Vue d’ensemble

- Base de données : `medical_db`
- Collection principale : `patients`
- Grain : 1 document par ligne du fichier CSV `data/healthcare_dataset.csv`.

Chaque document représente un patient pour une admission donnée (combinaison `Name` + `Date of Admission` + `Hospital`).

## 2. Champs du document `patients`

| Champ               | Type MongoDB | Source CSV            | Description                                                  |
|---------------------|-------------:|------------------------|--------------------------------------------------------------|
| `_id`               | ObjectId     | (généré par MongoDB)   | Identifiant unique du document.                             |
| `Name`              | String       | `Name`                 | Nom complet du patient, tel que présent dans le CSV.        |
| `Age`               | Int32        | `Age`                  | Âge du patient en années.                                   |
| `Gender`            | String       | `Gender`               | Sexe du patient.                                            |
| `Blood Type`        | String       | `Blood Type`           | Groupe sanguin (A+, O-, etc.).                             |
| `Medical Condition` | String       | `Medical Condition`    | Pathologie principale (Cancer, Diabetes, Hypertension, …). |
| `Date of Admission` | String       | `Date of Admission`    | Date d’admission au format `YYYY-MM-DD` (stockée en chaîne).|
| `Doctor`            | String       | `Doctor`               | Médecin responsable.                                        |
| `Hospital`          | String       | `Hospital`             | Nom de l’établissement.                                     |
| `Insurance Provider`| String       | `Insurance Provider`   | Assurance / mutuelle.                                       |
| `Billing Amount`    | Double       | `Billing Amount`       | Montant de facturation (nombre décimal).                    |
| `Room Number`       | Int32        | `Room Number`          | Numéro de chambre.                                          |
| `Admission Type`    | String       | `Admission Type`       | Type d’admission (Urgent, Emergency, Elective, …).          |
| `Discharge Date`    | String       | `Discharge Date`       | Date de sortie au format `YYYY-MM-DD` (chaîne).             |
| `Medication`        | String       | `Medication`           | Médicament principal prescrit.                              |
| `Test Results`      | String       | `Test Results`         | Résultat des tests (Normal, Abnormal, Inconclusive, …).     |

> Remarque : les dates sont actuellement stockées comme chaînes (`String`) au format `YYYY-MM-DD`, conformément au fichier CSV. Une évolution possible serait de les convertir en 
véritables types `Date` MongoDB lors de la migration.

## 3. Contraintes et choix de modélisation

- **Clé primaire** : `_id` est géré automatiquement par MongoDB.
- **Doublons métier** : le triplet (`Name`, `Date of Admission`, `Hospital`) n’est pas unique.  
  Le script `tests/data_quality.py` met en évidence environ 5 500 doublons sur ce triplet (~10 % des lignes).  
  Dans ce projet, ces doublons potentiels sont documentés mais non supprimés, faute d’identifiant patient unique.
- **Types** : les types utilisés sont alignés avec les types inférés par `pandas` lors de la lecture du CSV (entiers, flottants, chaînes).

## 4. Idées d’index (pistes)

Pour améliorer les performances de requêtage, on pourrait ajouter les index suivants :

- Index sur `Medical Condition` (analyses par pathologie).
- Index sur `Doctor` ou `Hospital` (analyse d’activité par médecin / établissement).
- Index composé sur (`Name`, `Date of Admission`, `Hospital`) pour accélérer les recherches de séjours et mieux gérer les doublons.
