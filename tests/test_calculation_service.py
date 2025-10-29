import pytest
from app.services.calculation_service import CalculationService
from app.models.slot import Slot


def test_calculate_week_totals():
    """Test du calcul des totaux hebdomadaires"""
    # Créer des créneaux de test
    slots = [
        Slot(day_index=0, start_min=540, duration_min=120, title="Test 1", category="o"),  # 2h lundi
        Slot(day_index=0, start_min=660, duration_min=60, title="Test 2", category="p"),   # 1h lundi
        Slot(day_index=1, start_min=540, duration_min=90, title="Test 3", category="e"),   # 1.5h mardi
        Slot(day_index=2, start_min=600, duration_min=45, title="Test 4", category="m"),   # 0.75h mercredi (indéterminé)
    ]
    
    totals = CalculationService.calculate_week_totals(slots)
    
    assert totals.per_day[0] == 3.0  # Lundi: 2h + 1h
    assert totals.per_day[1] == 1.5  # Mardi: 1.5h
    assert totals.per_day[2] == 0.75  # Mercredi: 0.75h
    assert totals.week_total == 5.25  # Total: 5.25h
    assert totals.indetermine == 0.75  # Indéterminé: 0.75h (catégorie 'm')


def test_calculate_category_repartition():
    """Test du calcul de la répartition par catégorie"""
    slots = [
        Slot(day_index=0, start_min=540, duration_min=120, title="Admin", category="a"),      # 2h admin
        Slot(day_index=0, start_min=660, duration_min=60, title="Prestation", category="p"),  # 1h prestation
        Slot(day_index=1, start_min=540, duration_min=90, title="École", category="e"),       # 1.5h école
        Slot(day_index=1, start_min=630, duration_min=30, title="Compét", category="c"),      # 0.5h compétition
    ]
    
    repartition = CalculationService.calculate_category_repartition(slots)
    
    assert repartition.a == 2.0    # Administratif
    assert repartition.p == 1.0    # Prestation
    assert repartition.e == 1.5    # École
    assert repartition.c == 0.5    # Compétition
    assert repartition.o == 0.0    # Ouverture (pas de créneaux)


def test_check_slot_overlap():
    """Test de la détection de chevauchement"""
    existing_slots = [
        Slot(id=1, day_index=0, start_min=540, duration_min=120, title="Existing", category="o"),  # 9h-11h
    ]
    
    # Créneau qui chevauche
    overlapping_slot = Slot(day_index=0, start_min=600, duration_min=60, title="Overlap", category="p")  # 10h-11h
    assert CalculationService.check_slot_overlap(existing_slots, overlapping_slot) == True
    
    # Créneau qui ne chevauche pas
    non_overlapping_slot = Slot(day_index=0, start_min=660, duration_min=60, title="No overlap", category="p")  # 11h-12h
    assert CalculationService.check_slot_overlap(existing_slots, non_overlapping_slot) == False
    
    # Créneau sur un autre jour
    other_day_slot = Slot(day_index=1, start_min=540, duration_min=120, title="Other day", category="p")
    assert CalculationService.check_slot_overlap(existing_slots, other_day_slot) == False


def test_get_category_legend():
    """Test de la récupération de la légende des catégories"""
    legend = CalculationService.get_category_legend()
    
    assert 'a' in legend
    assert legend['a']['label'] == 'Administratif/gestion'
    assert legend['a']['color'] == '#49B675'
    
    assert 'p' in legend
    assert legend['p']['label'] == 'Prestation/événement'
    assert legend['p']['color'] == '#40E0D0'
    
    # Vérifier que toutes les catégories sont présentes
    expected_categories = ['a', 'p', 'e', 'c', 'o', 'l', 'm', 's']
    for cat in expected_categories:
        assert cat in legend
        assert 'label' in legend[cat]
        assert 'color' in legend[cat]