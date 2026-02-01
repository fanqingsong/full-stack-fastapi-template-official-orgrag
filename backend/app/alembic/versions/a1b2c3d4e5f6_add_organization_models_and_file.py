"""Add organization models and file permissions

Revision ID: a1b2c3d4e5f6
Revises: 83832351eb7e
Create Date: 2026-02-01

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '83832351eb7e'
branch_labels = None
depends_on = None


def upgrade():
    # Create businessunit table
    op.create_table(
        'businessunit',
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('code', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('name')
    )

    # Create function table
    op.create_table(
        'function',
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column('code', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('business_unit_id', sa.Uuid(), nullable=False),
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['business_unit_id'], ['businessunit.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Add columns to user table
    op.add_column('user', sa.Column('business_unit_id', sa.Uuid(), nullable=True))
    op.add_column('user', sa.Column('function_id', sa.Uuid(), nullable=True))
    op.create_foreign_key('fk_user_bu', 'user', 'businessunit', ['business_unit_id'], ['id'])
    op.create_foreign_key('fk_user_function', 'user', 'function', ['function_id'], ['id'])

    # Add columns to file table
    op.add_column('file', sa.Column('responsible_function_id', sa.Uuid(), nullable=True))
    op.add_column('file', sa.Column('visible_bu_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(
        'fk_file_responsible_function',
        'file', 'function',
        ['responsible_function_id'], ['id']
    )
    op.create_foreign_key(
        'fk_file_visible_bu',
        'file', 'businessunit',
        ['visible_bu_id'], ['id']
    )

    # Create file-function link table for many-to-many
    op.create_table(
        'filefunctionlink',
        sa.Column('file_id', sa.Uuid(), nullable=False),
        sa.Column('function_id', sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['file.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['function_id'], ['function.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('file_id', 'function_id')
    )


def downgrade():
    op.drop_table('filefunctionlink')

    op.drop_constraint('fk_file_visible_bu', 'file', type_='foreignkey')
    op.drop_constraint('fk_file_responsible_function', 'file', type_='foreignkey')
    op.drop_column('file', 'visible_bu_id')
    op.drop_column('file', 'responsible_function_id')

    op.drop_constraint('fk_user_function', 'user', type_='foreignkey')
    op.drop_constraint('fk_user_bu', 'user', type_='foreignkey')
    op.drop_column('user', 'function_id')
    op.drop_column('user', 'business_unit_id')

    op.drop_table('function')
    op.drop_table('businessunit')
