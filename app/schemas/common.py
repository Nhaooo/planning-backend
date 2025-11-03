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
    a: float  # Administratif/gestion
    p: float  # Prestation/événement
    e: float  # École d'escalade
    c: float  # Groupes compétition
    o: float  # Ouverture
    l: float  # Loisir
    m: float  # Mise en place / Rangement
    s: float  # Santé Adulte/Enfant


class CategoryRepartitionPercent(BaseModel):
    a: float
    p: float
    e: float
    c: float
    o: float
    l: float
    m: float
    s: float