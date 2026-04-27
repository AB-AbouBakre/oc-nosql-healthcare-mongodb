# Étude : migration vers le cloud AWS pour la base médicale MongoDB

## 1. Contexte et objectif

Le client dispose aujourd’hui de données médicales stockées dans des fichiers CSV volumineux et d’une base MongoDB déployée en local via Docker.  
L’objectif de cette étude est de présenter l’intérêt d’un passage au cloud, en particulier sur AWS, et de lister les principaux services qui pourraient être utilisés pour héberger 
MongoDB, stocker les données sources et assurer les sauvegardes et la supervision.

## 2. Intérêt du passage au cloud pour le client

Passer d’une infrastructure locale à une infrastructure cloud apporte plusieurs bénéfices :

- **Scalabilité** : possibilité d’augmenter ou de diminuer la capacité (stockage, CPU, RAM) en fonction de la volumétrie et du trafic, sans racheter de matériel.
- **Haute disponibilité** : les services managés d’AWS peuvent être déployés sur plusieurs zones de disponibilité pour réduire le risque d’indisponibilité.
- **Réduction de la gestion matérielle** : AWS gère les datacenters, l’infrastructure réseau et le stockage sous-jacent ; le client se concentre sur ses données et ses applications. 
[web:362]
- **Modèle de coût à l’usage** : facturation en fonction de l’utilisation réelle (stockage consommé, puissance de calcul, transferts), avec la possibilité de fixer des budgets et des 
alertes.
- **Sécurité et conformité** : services de sécurité intégrés (chiffrement, contrôle d’accès, journalisation) pouvant aider à répondre à des exigences réglementaires, sous réserve d’une 
configuration correcte.

## 3. Stockage des données : AWS et le cloud storage

### 3.1. Notion de stockage dans le cloud

Le stockage dans le cloud consiste à confier le stockage de ses données à un fournisseur cloud, qui les héberge dans ses datacenters et les rend accessibles via Internet ou un réseau 
privé.  
Cela permet de bénéficier d’une capacité quasiment illimitée, ajustable à la demande, avec une gestion déléguée de la disponibilité, de la sécurité et de la durabilité des données. 
[web:362]

### 3.2. Amazon S3 pour les fichiers CSV et les sauvegardes

Pour ce projet, **Amazon S3 (Simple Storage Service)** peut jouer plusieurs rôles : [web:369][web:366]

- Stockage des fichiers CSV sources utilisés pour alimenter MongoDB.
- Stockage des exports ou sauvegardes de la base (dumps MongoDB, snapshots chiffrés).
- Mise à disposition des datasets pour d’autres applications (BI, data science, etc.).

S3 est un stockage d’objets très durable et hautement disponible, facturé au volume stocké et au nombre d’accès.

## 4. Services AWS pour MongoDB

### 4.1. Amazon DocumentDB (compatible MongoDB)

AWS ne propose pas “MongoDB sur RDS” mais un service managé appelé **Amazon DocumentDB (compatible MongoDB)**. [web:367][web:370]

- Il expose une API compatible avec MongoDB, ce qui permet de réutiliser en grande partie les drivers et outils MongoDB existants.
- C’est un service managé : AWS gère les mises à jour, le cluster, la réplication, les sauvegardes automatiques et une partie de la sécurité.
- Le stockage peut être automatiquement étendu en fonction des besoins, sans intervention sur les serveurs.

Dans le contexte du client, DocumentDB permettrait de bénéficier d’un service proche de MongoDB sans gérer soi-même les serveurs ou le cluster.

### 4.2. MongoDB en conteneur Docker sur Amazon ECS

Une autre approche consiste à déployer MongoDB dans un conteneur Docker sur **Amazon ECS (Elastic Container Service)**. [web:368][web:371]

- ECS est un service d’orchestration de conteneurs qui permet de déployer, gérer et faire évoluer des applications packagées en images Docker.
- On définit une ou plusieurs tâches (tasks) qui décrivent les conteneurs à exécuter (par exemple : un conteneur MongoDB, un conteneur d’application), puis ECS se charge de les lancer sur 
une infrastructure gérée par AWS (EC2 ou Fargate).
- Cette approche offre plus de contrôle sur la configuration de MongoDB (version exacte, options, fichiers de configuration), mais laisse au client la responsabilité de la haute 
disponibilité, des sauvegardes et de certaines tâches d’administration.

Pour ce projet, le conteneur MongoDB utilisé en local via `docker-compose` pourrait être déployé sur ECS avec peu de modifications, ce qui facilite une migration progressive.

## 5. Création d’un compte AWS et gestion des coûts

### 5.1. Création d’un compte AWS

Les grandes étapes pour créer un compte AWS sont les suivantes :

- Se rendre sur le site aws.amazon.com et cliquer sur “Créer un compte”.
- Renseigner une adresse e-mail, un mot de passe et un identifiant de compte.
- Fournir des informations de contact (profil personnel ou professionnel).
- Ajouter un moyen de paiement (carte bancaire) et vérifier l’identité.
- Se connecter à la console de gestion AWS, puis créer un utilisateur IAM pour l’utilisation quotidienne (bonne pratique : ne pas utiliser le compte root pour les opérations courantes).

### 5.2. Tarification et suivi des coûts

AWS adopte un modèle de tarification **pay-as-you-go**, où l’on paie en fonction de ce que l’on consomme (stockage, calcul, transferts, requêtes). [web:363][web:365]

Pour maîtriser les coûts, il est recommandé de :

- Activer la console de **Billing** pour suivre les dépenses.
- Définir des **budgets** et des alertes (AWS Budgets) pour être notifié en cas de dépassement.
- Utiliser autant que possible les offres d’essai et le **Free Tier** pour les environnements de test.

Dans le cadre de ce projet, il serait possible de limiter les coûts en utilisant de petites instances ou des environnements de test temporaires.

## 6. Sauvegardes et surveillance des bases sur AWS

### 6.1. Sauvegardes

Les sauvegardes peuvent être gérées de plusieurs façons :

- Avec un service managé comme DocumentDB, en utilisant les **backups automatiques** et les snapshots gérés par AWS.
- En exportant régulièrement les données MongoDB (par exemple avec `mongodump`) et en stockant les archives sur Amazon S3.
- En combinant ces approches avec des stratégies de rétention (conserver X jours/semaine/mois) pour équilibrer coûts et exigences réglementaires.

### 6.2. Supervision et alertes

La supervision des performances et de la disponibilité passe principalement par **Amazon CloudWatch** :

- Collecte des métriques (CPU, mémoire, I/O, connexions, latence).
- Mise en place d’**alarmes** (ex : taux d’erreurs, dépassement d’un seuil de CPU, baisse du nombre de nœuds disponibles).
- Centralisation des logs d’application et de base de données, afin de faciliter le diagnostic en cas d’incident.

Dans le contexte de ce projet, un premier niveau de supervision suffirait à surveiller l’état général du cluster et l’espace disque, avec quelques alertes simples.

## 7. Synthèse pour le client

Pour ce client, le passage au cloud AWS permettrait de :

- Mieux protéger ses données médicales grâce à une infrastructure managée et hautement disponible.
- Simplifier la gestion des sauvegardes et de la supervision.
- Faciliter l’évolution de la plateforme (volume de données, nouveaux usages d’analyse).

Deux approches principales peuvent être envisagées pour la base NoSQL :

1. **Service managé Amazon DocumentDB (compatible MongoDB)** : moins d’administration, mais un écart par rapport à MongoDB “pur”.
2. **MongoDB en conteneur Docker sur Amazon ECS** : plus de liberté de configuration, au prix d’un peu plus d’effort d’ops.

Cette étude ne réalise pas le déploiement effectif mais fournit les éléments nécessaires pour discuter des options avec le client et préparer une éventuelle migration.
