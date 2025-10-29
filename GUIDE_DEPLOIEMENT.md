# Guide de Déploiement Backend - Render

Ce guide vous accompagne pas-à-pas pour déployer le backend FastAPI sur Render avec PostgreSQL.

## 📋 Prérequis

- Compte GitHub avec le code du backend
- Compte Render (gratuit)
- Variables d'environnement configurées

## 🚀 Étape 1 : Préparation du Repository

### 1.1 Structure requise

Assurez-vous que votre repository contient :
```
planning-backend/
├── app/                 # Code de l'application
├── alembic/            # Migrations
├── requirements.txt    # Dépendances Python
├── seed.py            # Données de démonstration
├── alembic.ini        # Configuration Alembic
└── README.md          # Documentation
```

### 1.2 Fichier de démarrage

Créez un fichier `start.sh` (optionnel) :
```bash
#!/bin/bash
# Appliquer les migrations
alembic upgrade head

# Démarrer l'application
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 🗄️ Étape 2 : Base de Données PostgreSQL

### 2.1 Créer la base de données

1. Connectez-vous à [Render](https://render.com)
2. Cliquez sur **"New +"** → **"PostgreSQL"**
3. Configurez :
   - **Name** : `planning-postgres`
   - **Database** : `planning_db`
   - **User** : `planning_user`
   - **Region** : Europe (Frankfurt) pour de meilleures performances
   - **Plan** : Free (1 Go, expire après 30 jours)

4. Cliquez sur **"Create Database"**

### 2.2 Récupérer l'URL de connexion

1. Une fois créée, allez dans l'onglet **"Connect"**
2. Copiez l'**External Database URL** :
   ```
   postgresql://planning_user:password@dpg-xxxxx-a.frankfurt-postgres.render.com/planning_db
   ```

⚠️ **Important** : Notez cette URL, elle sera nécessaire pour l'application.

## 🌐 Étape 3 : Web Service

### 3.1 Créer le service web

1. Retour au dashboard Render
2. Cliquez sur **"New +"** → **"Web Service"**
3. Connectez votre repository GitHub
4. Sélectionnez le repository `planning-backend`

### 3.2 Configuration du service

**Paramètres de base :**
- **Name** : `planning-backend`
- **Region** : Europe (Frankfurt)
- **Branch** : `main`
- **Root Directory** : `planning-backend` (si dans un sous-dossier)
- **Runtime** : `Python 3`

**Commandes de build et démarrage :**
- **Build Command** :
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command** :
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### 3.3 Variables d'environnement

Dans la section **"Environment Variables"**, ajoutez :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `DATABASE_URL` | `postgresql://...` | URL de votre base PostgreSQL |
| `ADMIN_PIN` | `1234` | PIN d'administration |
| `BACKUP_SECRET` | `your-backup-secret-key` | Clé pour les backups |
| `SECRET_KEY` | `your-jwt-secret-key` | Clé pour JWT |
| `CORS_ORIGINS` | `https://yourusername.github.io` | Domaines autorisés |
| `ALGORITHM` | `HS256` | Algorithme JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Durée des tokens |

### 3.4 Finaliser la création

1. Cliquez sur **"Create Web Service"**
2. Le déploiement commence automatiquement
3. Attendez que le statut passe à **"Live"**

## 🔧 Étape 4 : Configuration Post-Déploiement

### 4.1 Appliquer les migrations

1. Dans votre service Render, allez dans **"Shell"**
2. Exécutez :
   ```bash
   alembic upgrade head
   ```

### 4.2 Injecter les données de démonstration

```bash
python seed.py
```

### 4.3 Tester l'API

Votre API est maintenant accessible à :
```
https://planning-backend-xxxx.onrender.com
```

Testez les endpoints :
```bash
# Health check
curl https://planning-backend-xxxx.onrender.com/api/v1/health

# Documentation
https://planning-backend-xxxx.onrender.com/docs
```

## 🔄 Étape 5 : Déploiement Automatique

### 5.1 Auto-deploy depuis GitHub

Render redéploie automatiquement à chaque push sur `main`.

### 5.2 Webhook (optionnel)

Pour déclencher des déploiements depuis d'autres sources :
1. Allez dans **"Settings"** → **"Build & Deploy"**
2. Copiez l'**Auto-Deploy Hook URL**

## 📊 Étape 6 : Monitoring et Logs

### 6.1 Logs en temps réel

Dans votre service Render :
1. Onglet **"Logs"** pour voir les logs en temps réel
2. Filtrez par niveau (INFO, ERROR, etc.)

### 6.2 Métriques

1. Onglet **"Metrics"** pour voir :
   - CPU et mémoire
   - Requêtes par minute
   - Temps de réponse

### 6.3 Alertes

Configurez des alertes pour :
- Service down
- Erreurs 5xx
- Utilisation mémoire élevée

## 🔐 Étape 7 : Sécurité

### 7.1 Variables d'environnement sensibles

- Utilisez des mots de passe forts
- Changez les clés par défaut
- Ne commitez jamais les secrets

### 7.2 CORS

Limitez `CORS_ORIGINS` aux domaines nécessaires :
```
https://yourusername.github.io,https://your-custom-domain.com
```

### 7.3 Rate limiting

L'application inclut un rate limiting basique. Pour plus de protection, utilisez Cloudflare.

## 💾 Étape 8 : Backups

### 8.1 Configuration GitHub Actions

1. Dans votre repository, allez dans **"Settings"** → **"Secrets and variables"** → **"Actions"**
2. Ajoutez les secrets :
   - `RENDER_APP_URL` : `https://planning-backend-xxxx.onrender.com`
   - `BACKUP_SECRET` : Même valeur que dans Render
   - `BACKUP_TOKEN` : Token GitHub avec permissions repo

### 8.2 Test du backup

Déclenchez manuellement le workflow :
1. Allez dans **"Actions"** → **"Database Backup"**
2. Cliquez sur **"Run workflow"**

## 🚨 Dépannage

### Problème : Service ne démarre pas

**Vérifiez :**
1. Les logs dans Render
2. La syntaxe de `requirements.txt`
3. Les variables d'environnement

**Solution :**
```bash
# Dans le shell Render
pip list  # Vérifier les packages installés
python -c "import app.main"  # Tester l'import
```

### Problème : Erreur de base de données

**Vérifiez :**
1. L'URL de connexion PostgreSQL
2. Que la base est accessible
3. Les migrations sont appliquées

**Solution :**
```bash
# Tester la connexion
python -c "from app.database import engine; print(engine.execute('SELECT 1').scalar())"

# Réappliquer les migrations
alembic upgrade head
```

### Problème : CORS

**Symptômes :** Erreurs CORS dans le navigateur

**Solution :**
1. Vérifiez `CORS_ORIGINS` dans les variables d'environnement
2. Incluez le protocole (`https://`)
3. Pas de slash final

### Problème : Cold start lent

**Cause :** Render Free met en veille après 15 min d'inactivité

**Solutions :**
1. Utilisez un service de ping (UptimeRobot)
2. Passez au plan payant
3. Affichez un message "Réveil du serveur" côté frontend

## 📈 Optimisations

### Performance

1. **Connexions DB** : Configurez le pool de connexions
2. **Cache** : Ajoutez Redis si nécessaire
3. **CDN** : Utilisez Cloudflare pour les assets

### Monitoring avancé

1. **Sentry** : Pour le tracking d'erreurs
2. **New Relic** : Pour les performances
3. **Datadog** : Pour les métriques custom

## 🔄 Mise à jour

### Déploiement d'une nouvelle version

1. Push sur `main` → Déploiement automatique
2. Vérifiez les logs
3. Testez les endpoints critiques

### Rollback

En cas de problème :
1. Allez dans **"Deploys"**
2. Cliquez sur **"Redeploy"** sur une version précédente

## 📞 Support

- **Documentation Render** : https://render.com/docs
- **Status Render** : https://status.render.com
- **Community** : https://community.render.com

---

✅ **Votre backend est maintenant déployé et opérationnel !**

URL de votre API : `https://planning-backend-xxxx.onrender.com`
Documentation : `https://planning-backend-xxxx.onrender.com/docs`