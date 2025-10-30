#!/usr/bin/env python3
"""
Script d'initialisation des données de référence pour la base de données
"""

import psycopg2
import os

# URL de la base de données de production avec SSL
DATABASE_URL = "postgresql://planning_db_user:Ey8Ey8Ey8Ey8Ey8Ey8Ey8Ey8Ey8@dpg-cs8qlhbtq21c73a8dn50-a.oregon-postgres.render.com/planning_db?sslmode=require"

def init_reference_data():
    """Initialise les données de référence directement en SQL"""
    
    try:
        print("🚀 Connexion à la base de données...")
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("📅 Initialisation des types de semaine...")
        
        # Créer les WeekKind
        week_kinds_sql = """
        INSERT INTO week_kind (id, kind) VALUES 
        (1, 'type'),
        (2, 'current'), 
        (3, 'next'),
        (4, 'vacation')
        ON CONFLICT (id) DO NOTHING;
        """
        
        cur.execute(week_kinds_sql)
        print("  ✅ Types de semaine créés")
        
        # Créer les VacationPeriod
        print("🏖️ Initialisation des périodes de vacances...")
        vacation_periods_sql = """
        INSERT INTO vacation_period (id, period) VALUES 
        (1, 'TOUSSAINT'),
        (2, 'NOEL'),
        (3, 'PAQUES'),
        (4, 'ETE')
        ON CONFLICT (id) DO NOTHING;
        """
        
        cur.execute(vacation_periods_sql)
        print("  ✅ Périodes de vacances créées")
        
        # Commit les changements
        conn.commit()
        
        # Vérification
        cur.execute("SELECT COUNT(*) FROM week_kind")
        kinds_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM vacation_period")
        vacations_count = cur.fetchone()[0]
        
        print(f"✅ Données de référence initialisées avec succès !")
        print(f"📊 Total: {kinds_count} types de semaine, {vacations_count} périodes de vacances")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        if 'conn' in locals():
            conn.rollback()
        raise
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    init_reference_data()