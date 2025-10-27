"""
create ar_ap tables and enums
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0008_ar_ap_tables'
down_revision = '0007_create_mv_trial_balance'
branch_labels = None
depends_on = None


def upgrade():
    # Enums
    op.execute("CREATE TYPE partner_type AS ENUM ('customer','supplier');")
    op.execute("CREATE TYPE invoice_type AS ENUM ('sale','purchase');")
    op.execute("CREATE TYPE invoice_status AS ENUM ('draft','open','partial','paid','cancelled');")
    op.execute("CREATE TYPE payment_method AS ENUM ('cash','bank','check','gateway','other');")
    op.execute("CREATE TYPE check_status AS ENUM ('issued','received','deposited','cleared','bounced','returned');")

    # partners
    op.create_table(
        'partners',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('partner_type', sa.Enum('customer','supplier', name='partner_type'), nullable=False),
        sa.Column('tax_id', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=64), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('credit_limit', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_partners_name', 'partners', ['name'])

    # invoices
    op.create_table(
        'invoices',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_no', sa.String(length=64), nullable=False),
        sa.Column('series', sa.String(length=8), nullable=True),
        sa.Column('invoice_type', sa.Enum('sale','purchase', name='invoice_type'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('subtotal', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('tax_total', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('total_amount', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('balance_amount', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('exchange_rate', sa.Numeric(18,6), nullable=False, server_default='1'),
        sa.Column('status', sa.Enum('draft','open','partial','paid','cancelled', name='invoice_status'), nullable=False, server_default='draft'),
        sa.Column('created_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_invoices_date', 'invoices', ['date'])
    op.create_index('ix_invoices_due_date', 'invoices', ['due_date'])
    op.create_unique_constraint('uq_invoices_company_series_no', 'invoices', ['company_id','series','invoice_no'])
    op.create_check_constraint('ck_invoice_total_non_negative', 'invoices', 'total_amount >= 0')
    op.create_check_constraint('ck_invoice_balance_non_negative', 'invoices', 'balance_amount >= 0')

    # invoice_lines
    op.create_table(
        'invoice_lines',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('invoice_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('line_no', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('qty', sa.Numeric(18,4), nullable=False, server_default='0'),
        sa.Column('unit_price', sa.Numeric(18,4), nullable=False, server_default='0'),
        sa.Column('tax_rate', sa.Numeric(5,2), nullable=False, server_default='0'),
        sa.Column('line_total', sa.Numeric(18,4), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint('uq_invoice_lines_invoice_line_no', 'invoice_lines', ['invoice_id','line_no'])
    op.create_check_constraint('ck_invoice_line_qty_non_negative', 'invoice_lines', 'qty >= 0')

    # payments
    op.create_table(
        'payments',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('invoice_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('method', sa.Enum('cash','bank','check','gateway','other', name='payment_method'), nullable=False),
        sa.Column('reference', sa.String(length=128), nullable=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('posted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_by', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_payments_date', 'payments', ['date'])
    op.create_check_constraint('ck_payment_amount_positive', 'payments', 'amount > 0')

    # checks
    op.create_table(
        'checks',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('partner_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('check_no', sa.String(length=64), nullable=False),
        sa.Column('bank_name', sa.String(length=128), nullable=True),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=True),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('issued','received','deposited','cleared','bounced','returned', name='check_status'), nullable=False, server_default='issued'),
        sa.Column('related_payment_id', sa.dialects.postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint('uq_checks_company_check_no', 'checks', ['company_id','check_no'])
    op.create_check_constraint('ck_check_amount_positive', 'checks', 'amount > 0')
    op.create_index('ix_checks_due_date', 'checks', ['due_date'])

    # Optional materialized view for partner_ledger_view (skeleton)
    op.execute("""
    CREATE MATERIALIZED VIEW IF NOT EXISTS partner_ledger_view AS
    SELECT p.id as partner_id, p.name as partner_name, p.company_id,
      COALESCE(SUM(i.total_amount),0) as invoices_total,
      COALESCE(SUM(i.balance_amount),0) as invoices_balance,
      COALESCE(SUM(pay.amount),0) as payments_total
    FROM partners p
    LEFT JOIN invoices i ON i.partner_id = p.id AND i.status <> 'cancelled'
    LEFT JOIN payments pay ON pay.partner_id = p.id
    GROUP BY p.id, p.name, p.company_id;
    """)


def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS partner_ledger_view;")
    op.drop_index('ix_checks_due_date', table_name='checks')
    op.drop_constraint('uq_checks_company_check_no', 'checks', type_='unique')
    op.drop_table('checks')

    op.drop_constraint('ck_payment_amount_positive', 'payments', type_='check')
    op.drop_index('ix_payments_date', table_name='payments')
    op.drop_table('payments')

    op.drop_constraint('uq_invoice_lines_invoice_line_no', 'invoice_lines', type_='unique')
    op.drop_table('invoice_lines')

    op.drop_constraint('uq_invoices_company_series_no', 'invoices', type_='unique')
    op.drop_index('ix_invoices_due_date', table_name='invoices')
    op.drop_index('ix_invoices_date', table_name='invoices')
    op.drop_table('invoices')

    op.drop_index('ix_partners_name', table_name='partners')
    op.drop_table('partners')

    op.execute('DROP TYPE IF EXISTS check_status;')
    op.execute('DROP TYPE IF EXISTS payment_method;')
    op.execute('DROP TYPE IF EXISTS invoice_status;')
    op.execute('DROP TYPE IF EXISTS invoice_type;')
    op.execute('DROP TYPE IF EXISTS partner_type;')
