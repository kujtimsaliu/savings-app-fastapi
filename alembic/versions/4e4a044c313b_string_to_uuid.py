from alembic import op

# revision identifiers, used by Alembic.
revision = '4e4a044c313b'
down_revision = '1c13f9e0a4c5'
branch_labels = None
depends_on = None

def upgrade():
    # This migration is now empty because we're creating the table with UUID from the start
    pass

def downgrade():
    # This migration is now empty because we're creating the table with UUID from the start
    pass