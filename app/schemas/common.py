from pydantic import BaseModel
from typing import Dict, List


class CategoryLegend(BaseModel):
    code: str
    label: str
    color: str


class WeekTotals(BaseModel):
    per_day: List[float]  # Heures par jour (7 jours)
    week_total: float
    indetermine: float


class CategoryRepartition(BaseModel):
    administratif: float  # Administratif/gestion
    prestation: float  # Prestation/événement
    ecole: float  # École d'escalade
    competition: float  # Groupes compétition
    ouverture: float  # Ouverture
    loisir: float  # Loisir
    mise_en_place: float  # Mise en place / Rangement
    sante: float  # Santé Adulte/Enfant


class CategoryRepartitionPercent(BaseModel):
    administratif: float
    prestation: float
    ecole: float
    competition: float
    ouverture: float
    loisir: float
    mise_en_place: float
    sante: float