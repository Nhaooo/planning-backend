from sqlalchemy.orm import Session
from app.models.week_kind import WeekKind, WeekKindEnum
from app.models.vacation_period import VacationPeriod, VacationPeriodEnum
from app.models.simple_slot import SimpleSlot
from app.database import Base, engine


class InitService:
    
    @staticmethod
    def init_reference_data(db: Session):
        """Initialise les données de référence si elles n'existent pas"""
        
        try:
            # Créer toutes les tables si elles n'existent pas
            print("🏗️ Création des tables...")
            Base.metadata.create_all(bind=engine)
            
            # Vérifier si les données existent déjà
            existing_kinds = db.query(WeekKind).count()
            existing_vacations = db.query(VacationPeriod).count()
            
            if existing_kinds > 0 and existing_vacations > 0:
                print("✅ Les données de référence existent déjà")
                return  # Données déjà présentes
            
            print("🚀 Initialisation des données de référence...")
            
            # Créer les WeekKind si nécessaire
            if existing_kinds == 0:
                week_kinds = [
                    WeekKind(id=1, kind=WeekKindEnum.TYPE.value),
                    WeekKind(id=2, kind=WeekKindEnum.CURRENT.value),
                    WeekKind(id=3, kind=WeekKindEnum.NEXT.value),
                    WeekKind(id=4, kind=WeekKindEnum.VACATION.value)
                ]
                
                for kind in week_kinds:
                    existing = db.query(WeekKind).filter(WeekKind.id == kind.id).first()
                    if not existing:
                        db.add(kind)
                        print(f"  ✅ WeekKind ajouté: {kind.kind} (ID: {kind.id})")
            
            # Créer les VacationPeriod si nécessaire
            if existing_vacations == 0:
                vacation_periods = [
                    VacationPeriod(id=1, period=VacationPeriodEnum.TOUSSAINT.value),
                    VacationPeriod(id=2, period=VacationPeriodEnum.NOEL.value),
                    VacationPeriod(id=3, period=VacationPeriodEnum.PAQUES.value),
                    VacationPeriod(id=4, period=VacationPeriodEnum.ETE.value)
                ]
                
                for period in vacation_periods:
                    existing = db.query(VacationPeriod).filter(VacationPeriod.id == period.id).first()
                    if not existing:
                        db.add(period)
                        print(f"  ✅ VacationPeriod ajouté: {period.period} (ID: {period.id})")
            
            # Commit les changements
            db.commit()
            print("✅ Données de référence initialisées avec succès !")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'initialisation des données de référence: {e}")
            db.rollback()
            # Ne pas lever l'exception pour ne pas empêcher le démarrage de l'app