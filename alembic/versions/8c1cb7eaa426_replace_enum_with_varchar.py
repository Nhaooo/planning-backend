"""replace_enum_with_varchar

Revision ID: 8c1cb7eaa426
Revises: 60a2d29b49ca
Create Date: 2025-10-30 18:27:02.236830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c1cb7eaa426'
down_revision = '60a2d29b49ca'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Supprimer toutes les données
    op.execute("DELETE FROM vacation_period")
    
    # Supprimer la colonne enum
    op.drop_column('vacation_period', 'period')
    
    # Supprimer l'enum complètement
    op.execute("DROP TYPE IF EXISTS vacationperiodenum")
    
    # Ajouter une colonne VARCHAR simple
    op.add_column('vacation_period', sa.Column('period', sa.String(50), nullable=False))
    
    # Ajouter contrainte unique
    op.create_unique_constraint('uq_vacation_period_period', 'vacation_period', ['period'])


def downgrade() -> None:
    # Supprimer la contrainte
    op.drop_constraint('uq_vacation_period_period', 'vacation_period', type_='unique')
    
    # Supprimer la colonne VARCHAR
    op.drop_column('vacation_period', 'period')
    
    # Recréer l'enum
    op.execute("CREATE TYPE vacationperiodenum AS ENUM ('Toussaint', 'Noel', 'Paques', 'Ete')")
    
    # Recréer la colonne enum
    op.add_column('vacation_period', sa.Column('period', sa.Enum('Toussaint', 'Noel', 'Paques', 'Ete', name='vacationperiodenum'), nullable=False))