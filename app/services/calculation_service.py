from typing import List, Dict
from app.models.slot import Slot
from app.schemas.common import WeekTotals, CategoryRepartition


class CalculationService:
    
    @staticmethod
    def calculate_week_totals(slots: List[Slot]) -> WeekTotals:
        """Calcule les totaux par jour et pour la semaine"""
        per_day = [0.0] * 7  # 7 jours
        week_total = 0.0
        indetermine = 0.0
        
        for slot in slots:
            hours = slot.duration_min / 60.0
            per_day[slot.day_index] += hours
            week_total += hours
            
            # Catégories considérées comme "indéterminées" (à ajuster selon les besoins)
            if slot.category in ['m']:  # Mise en place / Rangement
                indetermine += hours
        
        return WeekTotals(
            per_day=per_day,
            week_total=week_total,
            indetermine=indetermine
        )
    
    @staticmethod
    def calculate_category_repartition(slots: List[Slot]) -> CategoryRepartition:
        """Calcule la répartition par catégorie en heures"""
        repartition = {
            'a': 0.0,  # Administratif/gestion
            'p': 0.0,  # Prestation/événement
            'e': 0.0,  # École d'escalade
            'c': 0.0,  # Groupes compétition
            'o': 0.0,  # Ouverture
            'l': 0.0,  # Loisir
            'm': 0.0,  # Mise en place / Rangement
            's': 0.0,  # Santé Adulte/Enfant
        }
        
        for slot in slots:
            hours = slot.duration_min / 60.0
            if slot.category in repartition:
                repartition[slot.category] += hours
        
        return CategoryRepartition(**repartition)
    
    @staticmethod
    def check_slot_overlap(slots: List[Slot], new_slot: Slot, exclude_id: int = None) -> bool:
        """Vérifie s'il y a chevauchement entre les créneaux"""
        new_start = new_slot.start_min
        new_end = new_slot.start_min + new_slot.duration_min
        
        for slot in slots:
            if exclude_id and slot.id == exclude_id:
                continue
                
            if slot.day_index != new_slot.day_index:
                continue
                
            slot_start = slot.start_min
            slot_end = slot.start_min + slot.duration_min
            
            # Vérification du chevauchement
            if (new_start < slot_end and new_end > slot_start):
                return True
        
        return False
    
    @staticmethod
    def get_category_legend() -> Dict[str, Dict[str, str]]:
        """Retourne la légende des catégories"""
        return {
            'a': {'label': 'Administratif/gestion', 'color': '#49B675'},
            'p': {'label': 'Prestation/événement', 'color': '#40E0D0'},
            'e': {'label': 'École d\'escalade', 'color': '#A280FF'},
            'c': {'label': 'Groupes compétition', 'color': '#FF007F'},
            'o': {'label': 'Ouverture', 'color': '#FF2D2D'},
            'l': {'label': 'Loisir', 'color': '#FFD166'},
            'm': {'label': 'Mise en place / Rangement', 'color': '#FF9B54'},
            's': {'label': 'Santé Adulte/Enfant', 'color': '#FF8C42'},
        }