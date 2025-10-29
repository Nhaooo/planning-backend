"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create employees table
    op.create_table('employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('fullname', sa.String(length=100), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)
    op.create_index(op.f('ix_employees_slug'), 'employees', ['slug'], unique=True)

    # Create week_kind table
    op.create_table('week_kind',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.Enum('TYPE', 'CURRENT', 'NEXT', 'VACATION', name='weekkindenum'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('kind')
    )
    op.create_index(op.f('ix_week_kind_id'), 'week_kind', ['id'], unique=False)

    # Create vacation_period table
    op.create_table('vacation_period',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('period', sa.Enum('Toussaint', 'Noel', 'Paques', 'Ete', name='vacationperiodenum'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('period')
    )
    op.create_index(op.f('ix_vacation_period_id'), 'vacation_period', ['id'], unique=False)

    # Create weeks table
    op.create_table('weeks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('kind_id', sa.Integer(), nullable=False),
        sa.Column('vacation_id', sa.Integer(), nullable=True),
        sa.Column('week_start_date', sa.Date(), nullable=False),
        sa.Column('meta', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['kind_id'], ['week_kind.id'], ),
        sa.ForeignKeyConstraint(['vacation_id'], ['vacation_period.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'kind_id', 'vacation_id', 'week_start_date', name='unique_employee_week')
    )
    op.create_index(op.f('ix_weeks_id'), 'weeks', ['id'], unique=False)

    # Create slots table
    op.create_table('slots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('week_id', sa.Integer(), nullable=False),
        sa.Column('day_index', sa.Integer(), nullable=False),
        sa.Column('start_min', sa.Integer(), nullable=False),
        sa.Column('duration_min', sa.Integer(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=1), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.CheckConstraint('day_index >= 0 AND day_index <= 6', name='valid_day_index'),
        sa.CheckConstraint('start_min >= 0 AND start_min < 1440', name='valid_start_min'),
        sa.CheckConstraint('duration_min % 15 = 0', name='duration_multiple_15'),
        sa.CheckConstraint("category IN ('a','p','e','c','o','l','m','s')", name='valid_category'),
        sa.ForeignKeyConstraint(['week_id'], ['weeks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_slots_id'), 'slots', ['id'], unique=False)

    # Create notes table
    op.create_table('notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('week_id', sa.Integer(), nullable=False),
        sa.Column('hours_total', sa.DECIMAL(precision=5, scale=2), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('last_edit_by', sa.String(length=100), nullable=True),
        sa.Column('last_edit_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['week_id'], ['weeks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_id'), 'notes', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_notes_id'), table_name='notes')
    op.drop_table('notes')
    op.drop_index(op.f('ix_slots_id'), table_name='slots')
    op.drop_table('slots')
    op.drop_index(op.f('ix_weeks_id'), table_name='weeks')
    op.drop_table('weeks')
    op.drop_index(op.f('ix_vacation_period_id'), table_name='vacation_period')
    op.drop_table('vacation_period')
    op.drop_index(op.f('ix_week_kind_id'), table_name='week_kind')
    op.drop_table('week_kind')
    op.drop_index(op.f('ix_employees_slug'), table_name='employees')
    op.drop_index(op.f('ix_employees_id'), table_name='employees')
    op.drop_table('employees')