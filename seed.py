#!/usr/bin/env python3
"""
Script de seed pour initialiser la base de données avec des données de démonstration
"""

import sys
import os
from datetime import date, timedelta
from sqlalchemy.orm import Session

# Ajouter le répertoire de l'app au path
sys.path.append(os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models import *
from app.models.week_kind import WeekKindEnum
from app.models.vacation_period import VacationPeriodEnum


def create_seed_data():
    """Crée les données de démonstration"""
    db = SessionLocal()
    
    try:
        # 1. Créer les employés
        employees_data = [
            {"slug": "jeanne", "fullname": "Jeanne Dupont", "active": True},
            {"slug": "julien", "fullname": "Julien Martin", "active": True},
            {"slug": "lucas", "fullname": "Lucas Bernard", "active": True},
            {"slug": "melanie", "fullname": "Mélanie Rousseau", "active": True},
            {"slug": "raphael", "fullname": "Raphaël Moreau", "active": True},
        ]
        
        employees = []
        for emp_data in employees_data:
            employee = Employee(**emp_data)
            db.add(employee)
            employees.append(employee)
        
        db.commit()
        print(f"✓ Créé {len(employees)} employés")
        
        # 2. Créer les types de semaines
        week_kinds_data = [
            {"kind": WeekKindEnum.TYPE.value},
            {"kind": WeekKindEnum.CURRENT.value},
            {"kind": WeekKindEnum.NEXT.value},
            {"kind": WeekKindEnum.VACATION.value},
        ]
        
        week_kinds = []
        for wk_data in week_kinds_data:
            week_kind = WeekKind(**wk_data)
            db.add(week_kind)
            week_kinds.append(week_kind)
        
        db.commit()
        print(f"✓ Créé {len(week_kinds)} types de semaines")
        
        # 3. Créer les périodes de vacances
        vacation_periods_data = [
            {"period": VacationPeriodEnum.TOUSSAINT.value},
            {"period": VacationPeriodEnum.NOEL.value},
            {"period": VacationPeriodEnum.PAQUES.value},
            {"period": VacationPeriodEnum.ETE.value},
        ]
        
        vacation_periods = []
        for vp_data in vacation_periods_data:
            vacation_period = VacationPeriod(**vp_data)
            db.add(vacation_period)
            vacation_periods.append(vacation_period)
        
        db.commit()
        print(f"✓ Créé {len(vacation_periods)} périodes de vacances")
        
        # 4. Créer une semaine type pour Jeanne avec des créneaux de démonstration
        jeanne = employees[0]  # Jeanne
        week_type = week_kinds[0]  # TYPE
        
        # Lundi de la semaine courante
        today = date.today()
        monday = today - timedelta(days=today.weekday())
        
        week = Week(
            employee_id=jeanne.id,
            kind_id=week_type.id,
            week_start_date=monday,
            meta={"opening_hours": {"start": "09:00", "end": "22:00"}}
        )
        db.add(week)
        db.commit()
        
        # 5. Créer des créneaux de démonstration pour la semaine type
        demo_slots = [
            # Lundi
            {"day_index": 0, "start_min": 540, "duration_min": 120, "title": "Ouverture matin", "category": "o", "comment": "Ouverture de la salle"},
            {"day_index": 0, "start_min": 660, "duration_min": 90, "title": "École d'escalade enfants", "category": "e", "comment": "Groupe débutants 6-10 ans"},
            {"day_index": 0, "start_min": 750, "duration_min": 60, "title": "Administration", "category": "a", "comment": "Gestion planning"},
            {"day_index": 0, "start_min": 810, "duration_min": 180, "title": "Cours adultes", "category": "p", "comment": "Cours technique avancé"},
            
            # Mardi
            {"day_index": 1, "start_min": 540, "duration_min": 120, "title": "Ouverture matin", "category": "o"},
            {"day_index": 1, "start_min": 660, "duration_min": 120, "title": "Compétition jeunes", "category": "c", "comment": "Entraînement équipe compétition"},
            {"day_index": 1, "start_min": 780, "duration_min": 90, "title": "Loisir libre", "category": "l"},
            
            # Mercredi
            {"day_index": 2, "start_min": 480, "duration_min": 60, "title": "Mise en place", "category": "m", "comment": "Préparation matériel"},
            {"day_index": 2, "start_min": 540, "duration_min": 240, "title": "École d'escalade", "category": "e", "comment": "Journée complète enfants"},
            {"day_index": 2, "start_min": 780, "duration_min": 120, "title": "Cours adultes débutants", "category": "p"},
            
            # Jeudi
            {"day_index": 3, "start_min": 540, "duration_min": 120, "title": "Ouverture", "category": "o"},
            {"day_index": 3, "start_min": 660, "duration_min": 60, "title": "Santé adulte", "category": "s", "comment": "Escalade thérapeutique"},
            {"day_index": 3, "start_min": 720, "duration_min": 120, "title": "Prestation entreprise", "category": "p", "comment": "Team building"},
            
            # Vendredi
            {"day_index": 4, "start_min": 540, "duration_min": 120, "title": "Ouverture", "category": "o"},
            {"day_index": 4, "start_min": 660, "duration_min": 180, "title": "École d'escalade", "category": "e"},
            {"day_index": 4, "start_min": 840, "duration_min": 120, "title": "Loisir soirée", "category": "l"},
            
            # Samedi
            {"day_index": 5, "start_min": 480, "duration_min": 60, "title": "Mise en place", "category": "m"},
            {"day_index": 5, "start_min": 540, "duration_min": 300, "title": "Compétition", "category": "c", "comment": "Compétition régionale"},
            {"day_index": 5, "start_min": 840, "duration_min": 60, "title": "Rangement", "category": "m"},
            
            # Dimanche
            {"day_index": 6, "start_min": 600, "duration_min": 180, "title": "Loisir famille", "category": "l", "comment": "Escalade en famille"},
            {"day_index": 6, "start_min": 780, "duration_min": 60, "title": "Rangement", "category": "m"},
        ]
        
        slots = []
        for slot_data in demo_slots:
            slot = Slot(week_id=week.id, **slot_data)
            db.add(slot)
            slots.append(slot)
        
        db.commit()
        print(f"✓ Créé {len(slots)} créneaux de démonstration")
        
        # 6. Créer une note pour la semaine
        note = Note(
            week_id=week.id,
            hours_total=35.5,
            comments="Semaine type avec bonne répartition des activités. Attention à la compétition samedi.",
            last_edit_by="admin"
        )
        db.add(note)
        db.commit()
        print("✓ Créé note de démonstration")
        
        print("\n🎉 Données de seed créées avec succès !")
        print(f"   - {len(employees)} employés")
        print(f"   - {len(week_kinds)} types de semaines")
        print(f"   - {len(vacation_periods)} périodes de vacances")
        print(f"   - 1 semaine type avec {len(slots)} créneaux")
        print(f"   - 1 note de démonstration")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données de seed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Création des données de seed...")
    create_seed_data()