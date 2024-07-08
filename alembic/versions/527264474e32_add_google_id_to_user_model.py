"""Add google_id to User model

Revision ID: 527264474e32
Revises: 
Create Date: 2023-07-07 (use the actual date here)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '527264474e32'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create the enum type
    months_enum = postgresql.ENUM('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', name='months')
    months_enum.create(op.get_bind())

    # Alter the column type with explicit cast
    op.execute('ALTER TABLE budgets ALTER COLUMN month TYPE months USING month::months')

    # Add google_id column to users table
    op.add_column('users', sa.Column('google_id', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'users', ['google_id'])

    # Alter password and income columns to be nullable
    op.alter_column('users', 'password', nullable=True)
    op.alter_column('users', 'income', nullable=True)

def downgrade():
    # Remove google_id column from users table
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_column('users', 'google_id')

    # Revert password and income columns to be non-nullable
    op.alter_column('users', 'password', nullable=False)
    op.alter_column('users', 'income', nullable=False)

    # Change month column back to VARCHAR
    op.execute('ALTER TABLE budgets ALTER COLUMN month TYPE VARCHAR USING month::VARCHAR')

    # Drop the enum type
    op.execute('DROP TYPE months')