// init-mongo/init-users.js

db = db.getSiblingDB("medical_db");

// Compte applicatif (lecture / écriture sur medical_db)
db.createUser({
  user: "app_user",
  pwd: "AppUserPwd_2026", // par exemple 
  roles: [
    { role: "readWrite", db: "medical_db" }
  ]
});

// Compte analyste (lecture seule sur medical_db)
db.createUser({
  user: "analyst_user",
  pwd: "AnalystPwd_2026", // exemple de mot de passe
  roles: [
    { role: "read", db: "medical_db" }
  ]
});