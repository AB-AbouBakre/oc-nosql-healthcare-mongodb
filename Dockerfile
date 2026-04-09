FROM python:3.12-slim

WORKDIR /app

# Installer dépendances système minimales (optionnel, mais utile pour pandas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copier le code et les données
COPY src/ ./src
COPY data/ ./data

# Variable d'environnement pour l'URI MongoDB (valeur par défaut, surchargée par compose)
ENV MONGO_URI="mongodb://root:rootpassword@mongo:27017/medical_db?authSource=admin"

# Commande par défaut : lancer la migration
CMD ["python", "src/migrate.py"]
