from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.api.v1.api import api_router
from app.config import settings
from app.database import get_db
from app.services.init_service import InitService

app = FastAPI(
    title="Planning API",
    description="API pour la gestion des plannings hebdomadaires par quarts d'heure",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de sécurité pour les hosts de confiance
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # À restreindre en production
)

# Inclusion des routes API
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    print("🚀 Démarrage de l'application Planning API...")
    
    # Initialiser les données de référence
    db = next(get_db())
    try:
        InitService.init_reference_data(db)
    finally:
        db.close()


@app.get("/")
async def root():
    """Endpoint racine"""
    return {
        "message": "Planning API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)