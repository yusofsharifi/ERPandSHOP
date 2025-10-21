"""
create gl_sequence and gl_audit
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'gl_sequence',
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('last_number', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('company_id', 'fiscal_year')
    )
    op.create_table(
        'gl_audit',
        sa.Column('id', sa.UUID(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('resource_type', sa.String(length=100), nullable=False),
        sa.Column('resource_id', sa.UUID(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('performed_by', sa.UUID(), nullable=True),
        sa.Column('performed_at', sa.DateTime(timezone=True), nullable=True)
    )

def downgrade():
    op.drop_table('gl_audit')
    op.drop_table('gl_sequence')
