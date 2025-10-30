"""recreate_vacation_period_enum_with_correct_values

Revision ID: 60a2d29b49ca
Revises: ee4dce9d0e22
Create Date: 2025-10-30 18:22:19.733362

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60a2d29b49ca'
down_revision = 'ee4dce9d0e22'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Supprimer toutes les données de vacation_period
    op.execute("DELETE FROM vacation_period")
    
    # Supprimer la colonne qui utilise l'enum
    op.drop_column('vacation_period', 'period')
    
    # Supprimer l'ancien enum
    op.execute("DROP TYPE IF EXISTS vacationperiodenum")
    
    # Créer le nouvel enum avec les bonnes valeurs
    op.execute("CREATE TYPE vacationperiodenum AS ENUM ('Toussaint', 'Noel', 'Paques', 'Ete')")
    
    # Recréer la colonne avec le nouvel enum
    op.add_column('vacation_period', sa.Column('period', sa.Enum('Toussaint', 'Noel', 'Paques', 'Ete', name='vacationperiodenum'), nullable=False))
    
    # Ajouter la contrainte unique
    op.create_unique_constraint('uq_vacation_period_period', 'vacation_period', ['period'])


def downgrade() -> None:
    # Supprimer la contrainte unique
    op.drop_constraint('uq_vacation_period_period', 'vacation_period', type_='unique')
    
    # Supprimer la colonne
    op.drop_column('vacation_period', 'period')
    
    # Supprimer le nouvel enum
    op.execute("DROP TYPE IF EXISTS vacationperiodenum")
    
    # Recréer l'ancien enum (avec les anciennes valeurs)
    op.execute("CREATE TYPE vacationperiodenum AS ENUM ('TOUSSAINT', 'NOEL', 'PAQUES', 'ETE')")
    
    # Recréer la colonne avec l'ancien enum
    op.add_column('vacation_period', sa.Column('period', sa.Enum('TOUSSAINT', 'NOEL', 'PAQUES', 'ETE', name='vacationperiodenum'), nullable=False))