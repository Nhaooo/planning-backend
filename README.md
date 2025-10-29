# Planning Backend

API backend pour l'application de planning hebdomadaire par quarts d'heure.

## 🚀 Technologies

- **FastAPI** - Framework web moderne et rapide
- **SQLAlchemy 2.x** - ORM pour la base de données
- **Alembic** - Migrations de base de données
- **PostgreSQL** - Base de données principale
- **Pydantic v2** - Validation des données
- **pytest** - Tests unitaires

## 📋 Fonctionnalités

- ✅ Gestion des employés
- ✅ Plannings hebdomadaires par quarts d'heure
- ✅ Catégories de créneaux avec couleurs
- ✅ Calculs automatiques (totaux, répartitions)
- ✅ Vérification des chevauchements
- ✅ Authentification par PIN
- ✅ Backup/Restore automatisé
- ✅ API REST complète avec documentation

## 🏗️ Structure du projet

```
planning-backend/
├── app/
│   ├── api/v1/           # Endpoints API
│   ├── models/           # Modèles SQLAlchemy
│   ├── schemas/          # Schémas Pydantic
│   ├── services/         # Logique métier
│   ├── config.py         # Configuration
│   ├── database.py       # Configuration DB
│   └── main.py          # Application principale
├── alembic/             # Migrations
├── tests/               # Tests
├── seed.py             # Données de démonstration
└── requirements.txt    # Dépendances
```

## 🛠️ Installation locale

### Prérequis

- Python 3.11+
- PostgreSQL 14+

### Étapes

1. **Cloner le repository**
```bash
git clone <repo-url>
cd planning-backend
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les variables d'environnement**
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

5. **Créer la base de données**
```bash
# Créer la DB PostgreSQL
createdb planning_db

# Lancer les migrations
alembic upgrade head

# Injecter les données de démonstration
python seed.py
```

6. **Lancer le serveur de développement**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API sera accessible sur http://localhost:8000

## 📚 Documentation API

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🧪 Tests

```bash
# Lancer tous les tests
pytest

# Tests avec couverture
pytest --cov=app

# Tests spécifiques
pytest tests/test_calculation_service.py -v
```

## 🗄️ Modèle de données

### Tables principales

- **employees** : Employés (id, slug, fullname, active)
- **week_kind** : Types de semaines (type, current, next, vacation)
- **vacation_period** : Périodes de vacances (Toussaint, Noel, Paques, Ete)
- **weeks** : Semaines de planning
- **slots** : Créneaux de 15 minutes
- **notes** : Commentaires et métadonnées

### Catégories de créneaux

| Code | Libellé | Couleur |
|------|---------|---------|
| a | Administratif/gestion | #49B675 |
| p | Prestation/événement | #40E0D0 |
| e | École d'escalade | #A280FF |
| c | Groupes compétition | #FF007F |
| o | Ouverture | #FF2D2D |
| l | Loisir | #FFD166 |
| m | Mise en place / Rangement | #FF9B54 |
| s | Santé Adulte/Enfant | #FF8C42 |

## 🔐 Authentification

L'API utilise une authentification simple par PIN pour l'administration :

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"pin": "1234"}'
```

## 📊 Endpoints principaux

### Santé
- `GET /api/v1/health` - Vérification de santé

### Employés
- `GET /api/v1/employees` - Liste des employés
- `POST /api/v1/employees` - Créer un employé
- `PUT /api/v1/employees/{id}` - Modifier un employé

### Semaines et créneaux
- `GET /api/v1/weeks` - Liste des semaines (avec filtres)
- `GET /api/v1/weeks/{id}` - Détails d'une semaine
- `POST /api/v1/weeks/{id}/slots` - Créer un créneau
- `PATCH /api/v1/weeks/{id}/slots/{slot_id}` - Modifier un créneau

### Utilitaires
- `GET /api/v1/legend` - Légende des catégories
- `POST /api/v1/backup` - Créer un backup (protégé)
- `POST /api/v1/restore` - Restaurer un backup (protégé)

## 🔄 Migrations

```bash
# Créer une nouvelle migration
alembic revision --autogenerate -m "Description"

# Appliquer les migrations
alembic upgrade head

# Revenir en arrière
alembic downgrade -1
```

## 🌱 Données de démonstration

Le script `seed.py` crée :
- 5 employés (Jeanne, Julien, Lucas, Mélanie, Raphaël)
- Types de semaines et périodes de vacances
- Une semaine type complète avec créneaux variés

## 🚀 Déploiement

Voir [GUIDE_DEPLOIEMENT.md](./GUIDE_DEPLOIEMENT.md) pour les instructions détaillées de déploiement sur Render.

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 License

Ce projet est sous licence MIT.