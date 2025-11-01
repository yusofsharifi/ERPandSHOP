"""
create treasury tables and enums
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0009_treasury_tables'
down_revision = '0008_ar_ap_tables'
branch_labels = None
depends_on = None


def upgrade():
    # enums
    op.execute("CREATE TYPE treasury_source_type AS ENUM ('cash','bank','other');")
    op.execute("CREATE TYPE treasury_target_type AS ENUM ('cash','bank','other');")
    op.execute("CREATE TYPE reconciliation_status AS ENUM ('draft','matched','applied');")

    # cash_accounts
    op.create_table(
        'cash_accounts',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('balance', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint('uq_cash_accounts_company_code', 'cash_accounts', ['company_id','code'])
    op.create_index('ix_cash_accounts_company_code', 'cash_accounts', ['company_id','code'])

    # bank_accounts
    op.create_table(
        'bank_accounts',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_name', sa.String(length=255), nullable=False),
        sa.Column('account_number', sa.String(length=64), nullable=False),
        sa.Column('iban', sa.String(length=64), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('balance', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('routing_code', sa.String(length=64), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_bank_accounts_company_account', 'bank_accounts', ['company_id','account_number'])

    # treasury_transactions
    op.create_table(
        'treasury_transactions',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('source_type', sa.Enum('cash','bank','other', name='treasury_source_type'), nullable=False),
        sa.Column('source_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_type', sa.Enum('cash','bank','other', name='treasury_target_type'), nullable=False),
        sa.Column('target_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('exchange_rate', sa.Numeric(18,6), nullable=False, server_default='1'),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reference', sa.String(length=255), nullable=True),
        sa.Column('created_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('posted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('journal_entry_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_treasury_transactions_company_date', 'treasury_transactions', ['company_id','date'])
    op.create_index('ix_treasury_transactions_posted', 'treasury_transactions', ['posted'])

    # bank_reconciliations
    op.create_table(
        'bank_reconciliations',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bank_account_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('draft','matched','applied', name='reconciliation_status'), nullable=False, server_default='draft'),
        sa.Column('reconciliation_data', sa.JSON(), nullable=True),
        sa.Column('created_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('applied_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_bank_recon_account_period', 'bank_reconciliations', ['bank_account_id','period_start','period_end'])

    # bank_statement_lines
    op.create_table(
        'bank_statement_lines',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('reconciliation_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('bank_account_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('statement_date', sa.Date(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('reference', sa.String(length=255), nullable=True),
        sa.Column('matched', sa.Boolean(), nullable=False, server_default=sa.text('false')),
    )
    op.create_index('ix_bank_statement_lines_account_date', 'bank_statement_lines', ['bank_account_id','statement_date'])

    # audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('actor_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=128), nullable=False),
        sa.Column('object_type', sa.String(length=64), nullable=True),
        sa.Column('object_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_audit_logs_company_action', 'audit_logs', ['company_id','action'])


def downgrade():
    op.drop_index('ix_audit_logs_company_action', table_name='audit_logs')
    op.drop_table('audit_logs')

    op.drop_index('ix_bank_statement_lines_account_date', table_name='bank_statement_lines')
    op.drop_table('bank_statement_lines')

    op.drop_index('ix_bank_recon_account_period', table_name='bank_reconciliations')
    op.drop_table('bank_reconciliations')

    op.drop_index('ix_treasury_transactions_posted', table_name='treasury_transactions')
    op.drop_index('ix_treasury_transactions_company_date', table_name='treasury_transactions')
    op.drop_table('treasury_transactions')

    op.drop_index('ix_bank_accounts_company_account', table_name='bank_accounts')
    op.drop_table('bank_accounts')

    op.drop_index('ix_cash_accounts_company_code', table_name='cash_accounts')
    op.drop_constraint('uq_cash_accounts_company_code', 'cash_accounts', type_='unique')
    op.drop_table('cash_accounts')

    op.execute('DROP TYPE IF EXISTS reconciliation_status;')
    op.execute('DROP TYPE IF EXISTS treasury_target_type;')
    op.execute('DROP TYPE IF EXISTS treasury_source_type;')
