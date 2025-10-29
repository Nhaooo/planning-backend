from fastapi import APIRouter
from app.services.calculation_service import CalculationService

router = APIRouter()


@router.get("/")
def get_legend():
    """Récupère la légende des catégories avec couleurs et libellés"""
    return CalculationService.get_category_legend()