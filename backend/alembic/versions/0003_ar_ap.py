"""
AR/AP module: partners, invoices, invoice_lines, payments, checks, partner_ledger view

Revision ID: 0003_ar_ap
Revises: 0002_gl_full
Create Date: 2025-10-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0003_ar_ap'
down_revision = '0002_gl_full'
branch_labels = None
depends_on = None


def upgrade():
    # extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # enums
    partner_type = postgresql.ENUM('customer','supplier', name='partner_type')
    partner_type.create(op.get_bind(), checkfirst=True)

    invoice_status = postgresql.ENUM('draft','open','paid','cancelled','partial', name='invoice_status')
    invoice_status.create(op.get_bind(), checkfirst=True)

    invoice_type = postgresql.ENUM('sale','purchase', name='invoice_type')
    invoice_type.create(op.get_bind(), checkfirst=True)

    payment_method = postgresql.ENUM('cash','bank','check','gateway', name='payment_method')
    payment_method.create(op.get_bind(), checkfirst=True)

    check_status = postgresql.ENUM('issued','deposited','bounced','cleared', name='check_status')
    check_status.create(op.get_bind(), checkfirst=True)

    # partners
    op.create_table(
        'partners',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('partner_type', sa.Enum('customer','supplier', name='partner_type'), nullable=False),
        sa.Column('tax_id', sa.String(length=64), nullable=True),
        sa.Column('phone', sa.String(length=64), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('credit_limit', sa.Numeric(18,2), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_partners_name', 'partners', ['name'])

    # invoices
    op.create_table(
        'invoices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partners.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('invoice_no', sa.String(length=64), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('total_amount', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('balance_amount', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(length=16), nullable=False, server_default='USD'),
        sa.Column('status', sa.Enum('draft','open','paid','cancelled','partial', name='invoice_status'), nullable=False, server_default='draft'),
        sa.Column('invoice_type', sa.Enum('sale','purchase', name='invoice_type'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_unique_constraint('uq_invoices_invoice_no', 'invoices', ['invoice_no'])
    op.create_index('ix_invoices_date', 'invoices', ['date'])

    # invoice_lines
    op.create_table(
        'invoice_lines',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('invoices.id', ondelete='CASCADE'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('qty', sa.Numeric(18,4), nullable=False, server_default='1'),
        sa.Column('unit_price', sa.Numeric(18,4), nullable=False, server_default='0'),
        sa.Column('tax_rate', sa.Numeric(5,4), nullable=False, server_default='0'),
        sa.Column('line_total', sa.Numeric(18,2), nullable=False, server_default='0'),
    )
    op.create_check_constraint('ck_invoice_line_qty_non_negative', 'invoice_lines', 'qty >= 0')
    op.create_check_constraint('ck_invoice_line_price_non_negative', 'invoice_lines', 'unit_price >= 0')
    op.create_check_constraint('ck_invoice_line_tax_non_negative', 'invoice_lines', 'tax_rate >= 0')
    op.create_check_constraint('ck_invoice_line_total_non_negative', 'invoice_lines', 'line_total >= 0')

    # payments
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('invoice_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('invoices.id', ondelete='SET NULL'), nullable=True),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partners.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('method', sa.Enum('cash','bank','check','gateway', name='payment_method'), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('reference', sa.String(length=128), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_check_constraint('ck_payment_amount_positive', 'payments', 'amount > 0')
    op.create_index('ix_payments_date', 'payments', ['payment_date'])

    # checks
    op.create_table(
        'checks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('check_no', sa.String(length=64), nullable=False),
        sa.Column('bank', sa.String(length=128), nullable=True),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('issued','deposited','bounced','cleared', name='check_status'), nullable=False, server_default='issued'),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partners.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_check_constraint('ck_check_amount_positive', 'checks', 'amount > 0')
    op.create_unique_constraint('uq_checks_check_no', 'checks', ['check_no'])
    op.create_index('ix_checks_due_date', 'checks', ['due_date'])

    # sequences and triggers for invoice number
    op.execute("CREATE SEQUENCE IF NOT EXISTS ar_sale_invoice_no_seq;")
    op.execute("CREATE SEQUENCE IF NOT EXISTS ar_purchase_invoice_no_seq;")

    op.execute(
        """
        CREATE OR REPLACE FUNCTION ar_set_invoice_no()
        RETURNS trigger AS $$
        DECLARE
            next_no text;
        BEGIN
            IF NEW.invoice_no IS NULL OR NEW.invoice_no = '' THEN
                IF NEW.invoice_type = 'sale' THEN
                    next_no := 'S-' || to_char(nextval('ar_sale_invoice_no_seq'), 'FM000000');
                ELSE
                    next_no := 'P-' || to_char(nextval('ar_purchase_invoice_no_seq'), 'FM000000');
                END IF;
                NEW.invoice_no := next_no;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_set_invoice_no
        BEFORE INSERT ON invoices
        FOR EACH ROW EXECUTE FUNCTION ar_set_invoice_no();
        """
    )

    # totals and balance recalculation
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ar_recalc_invoice(p_invoice_id uuid)
        RETURNS void AS $$
        DECLARE
            v_total numeric(18,2);
            v_paid numeric(18,2);
            v_status text;
        BEGIN
            SELECT COALESCE(SUM(line_total + (line_total * tax_rate)), 0)
            INTO v_total
            FROM invoice_lines
            WHERE invoice_id = p_invoice_id;

            SELECT COALESCE(SUM(amount), 0)
            INTO v_paid
            FROM payments
            WHERE invoice_id = p_invoice_id;

            UPDATE invoices SET
                total_amount = v_total,
                balance_amount = GREATEST(v_total - v_paid, 0),
                status = CASE
                    WHEN status = 'cancelled' THEN 'cancelled'
                    WHEN v_total = 0 THEN 'draft'
                    WHEN GREATEST(v_total - v_paid, 0) = 0 THEN 'paid'
                    WHEN GREATEST(v_total - v_paid, 0) < v_total THEN 'partial'
                    ELSE 'open'
                END,
                updated_at = now()
            WHERE id = p_invoice_id;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # triggers to call recalc
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ar_recalc_after_invoice_line()
        RETURNS trigger AS $$
        BEGIN
            PERFORM ar_recalc_invoice(COALESCE(NEW.invoice_id, OLD.invoice_id));
            RETURN COALESCE(NEW, OLD);
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_recalc_after_invoice_line
        AFTER INSERT OR UPDATE OR DELETE ON invoice_lines
        FOR EACH ROW EXECUTE FUNCTION ar_recalc_after_invoice_line();
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION ar_recalc_after_payment()
        RETURNS trigger AS $$
        BEGIN
            IF TG_OP = 'DELETE' THEN
                IF OLD.invoice_id IS NOT NULL THEN
                    PERFORM ar_recalc_invoice(OLD.invoice_id);
                END IF;
                RETURN OLD;
            ELSE
                IF NEW.invoice_id IS NOT NULL THEN
                    PERFORM ar_recalc_invoice(NEW.invoice_id);
                END IF;
                RETURN NEW;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_recalc_after_payment
        AFTER INSERT OR UPDATE OR DELETE ON payments
        FOR EACH ROW EXECUTE FUNCTION ar_recalc_after_payment();
        """
    )

    # set initial balances when inserting invoices
    op.execute(
        """
        CREATE OR REPLACE FUNCTION ar_init_invoice()
        RETURNS trigger AS $$
        BEGIN
            PERFORM ar_recalc_invoice(NEW.id);
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_init_invoice
        AFTER INSERT ON invoices
        FOR EACH ROW EXECUTE FUNCTION ar_init_invoice();
        """
    )

    # partner_ledger view
    op.execute(
        """
        CREATE OR REPLACE VIEW partner_ledger AS
        SELECT i.partner_id,
               i.id AS doc_id,
               i.date AS txn_date,
               'invoice'::text AS source,
               CASE WHEN i.invoice_type = 'sale' THEN i.total_amount ELSE -i.total_amount END AS amount,
               i.currency
        FROM invoices i
        UNION ALL
        SELECT p.partner_id,
               p.id AS doc_id,
               p.payment_date AS txn_date,
               'payment'::text AS source,
               CASE
                    WHEN p.invoice_id IS NULL THEN -p.amount
                    ELSE (
                        CASE (SELECT inv.invoice_type FROM invoices inv WHERE inv.id = p.invoice_id)
                             WHEN 'sale' THEN -p.amount
                             ELSE p.amount
                        END
                    )
               END AS amount,
               COALESCE((SELECT inv.currency FROM invoices inv WHERE inv.id = p.invoice_id), 'USD') AS currency
        FROM payments p;
        """
    )


def downgrade():
    # drop view and triggers/functions
    op.execute("DROP VIEW IF EXISTS partner_ledger;")

    for trg in [
        'trg_init_invoice',
        'trg_recalc_after_payment',
        'trg_recalc_after_invoice_line',
        'trg_set_invoice_no'
    ]:
        op.execute(f"DROP TRIGGER IF EXISTS {trg} ON invoices;") if trg in ['trg_init_invoice','trg_set_invoice_no'] else None
        op.execute(f"DROP TRIGGER IF EXISTS {trg} ON payments;") if trg == 'trg_recalc_after_payment' else None
        op.execute(f"DROP TRIGGER IF EXISTS {trg} ON invoice_lines;") if trg == 'trg_recalc_after_invoice_line' else None

    for fn in [
        'ar_init_invoice',
        'ar_recalc_after_payment',
        'ar_recalc_after_invoice_line',
        'ar_recalc_invoice',
        'ar_set_invoice_no'
    ]:
        op.execute(f"DROP FUNCTION IF EXISTS {fn} CASCADE;")

    # drop sequences
    op.execute("DROP SEQUENCE IF EXISTS ar_sale_invoice_no_seq;")
    op.execute("DROP SEQUENCE IF EXISTS ar_purchase_invoice_no_seq;")

    # drop tables
    op.drop_index('ix_checks_due_date', table_name='checks')
    op.drop_constraint('uq_checks_check_no', 'checks', type_='unique')
    op.drop_constraint('ck_check_amount_positive', 'checks', type_='check')
    op.drop_table('checks')

    op.drop_index('ix_payments_date', table_name='payments')
    op.drop_constraint('ck_payment_amount_positive', 'payments', type_='check')
    op.drop_table('payments')

    op.drop_constraint('ck_invoice_line_total_non_negative', 'invoice_lines', type_='check')
    op.drop_constraint('ck_invoice_line_tax_non_negative', 'invoice_lines', type_='check')
    op.drop_constraint('ck_invoice_line_price_non_negative', 'invoice_lines', type_='check')
    op.drop_constraint('ck_invoice_line_qty_non_negative', 'invoice_lines', type_='check')
    op.drop_table('invoice_lines')

    op.drop_index('ix_invoices_date', table_name='invoices')
    op.drop_constraint('uq_invoices_invoice_no', 'invoices', type_='unique')
    op.drop_table('invoices')

    op.drop_index('ix_partners_name', table_name='partners')
    op.drop_table('partners')

    # enums
    for en in ['check_status','payment_method','invoice_type','invoice_status','partner_type']:
        enum_t = postgresql.ENUM(name=en)
        enum_t.drop(op.get_bind(), checkfirst=True)
