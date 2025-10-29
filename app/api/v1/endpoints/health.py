from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """Endpoint de vérification de santé de l'API"""
    return {"status": "ok"}