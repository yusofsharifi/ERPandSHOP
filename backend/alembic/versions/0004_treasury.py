"""
create treasury: cash_accounts, bank_accounts, treasury_transactions, bank_reconciliations

Revision ID: 0004_treasury
Revises: 0003_ar_ap
Create Date: 2025-10-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0004_treasury'
down_revision = '0003_ar_ap'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    source_type = postgresql.ENUM('cash','bank', name='source_type')
    source_type.create(op.get_bind(), checkfirst=True)

    recon_status = postgresql.ENUM('pending','reconciled','failed', name='recon_status')
    recon_status.create(op.get_bind(), checkfirst=True)

    # cash accounts
    op.create_table(
        'cash_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=True),
        sa.Column('balance', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('currency', sa.String(length=16), nullable=False, server_default='USD'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_cash_accounts_code', 'cash_accounts', ['code'])

    # bank accounts
    op.create_table(
        'bank_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('bank_name', sa.String(length=255), nullable=False),
        sa.Column('account_number', sa.String(length=128), nullable=False),
        sa.Column('currency', sa.String(length=16), nullable=False, server_default='USD'),
        sa.Column('balance', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_bank_accounts_account_number', 'bank_accounts', ['account_number'])

    # treasury transactions
    op.create_table(
        'treasury_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('source_type', sa.Enum('cash','bank', name='source_type'), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('target_type', sa.Enum('cash','bank', name='source_type'), nullable=False),
        sa.Column('target_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('currency', sa.String(length=16), nullable=False, server_default='USD'),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('reference', sa.String(length=255), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('check_id', sa.Integer(), sa.ForeignKey('checks.id', ondelete='SET NULL'), nullable=True),
    )
    op.create_check_constraint('ck_treasury_tx_amount_positive', 'treasury_transactions', 'amount > 0')
    op.create_index('ix_treasury_transactions_date', 'treasury_transactions', ['date'])

    # bank reconciliations
    op.create_table(
        'bank_reconciliations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('bank_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bank_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('status', sa.Enum('pending','reconciled','failed', name='recon_status'), nullable=False, server_default='pending'),
        sa.Column('reconciliation_data', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_bank_recon_bank_period', 'bank_reconciliations', ['bank_account_id','period_start','period_end'])

    # functions & triggers: adjust balances on insert/update/delete of treasury_transactions
    op.execute(
        """
        CREATE OR REPLACE FUNCTION treasury_apply_transaction() RETURNS trigger AS $$
        DECLARE
            src_type text;
            tgt_type text;
            amt numeric;
        BEGIN
            IF TG_OP = 'INSERT' THEN
                src_type := NEW.source_type;
                tgt_type := NEW.target_type;
                amt := NEW.amount;
                -- subtract from source
                IF src_type = 'cash' THEN
                    UPDATE cash_accounts SET balance = balance - amt WHERE id = NEW.source_id;
                ELSE
                    UPDATE bank_accounts SET balance = balance - amt WHERE id = NEW.source_id;
                END IF;
                -- add to target
                IF tgt_type = 'cash' THEN
                    UPDATE cash_accounts SET balance = balance + amt WHERE id = NEW.target_id;
                ELSE
                    UPDATE bank_accounts SET balance = balance + amt WHERE id = NEW.target_id;
                END IF;
                RETURN NEW;
            ELSIF TG_OP = 'DELETE' THEN
                src_type := OLD.source_type;
                tgt_type := OLD.target_type;
                amt := OLD.amount;
                -- reverse: add back to source, subtract from target
                IF src_type = 'cash' THEN
                    UPDATE cash_accounts SET balance = balance + amt WHERE id = OLD.source_id;
                ELSE
                    UPDATE bank_accounts SET balance = balance + amt WHERE id = OLD.source_id;
                END IF;
                IF tgt_type = 'cash' THEN
                    UPDATE cash_accounts SET balance = balance - amt WHERE id = OLD.target_id;
                ELSE
                    UPDATE bank_accounts SET balance = balance - amt WHERE id = OLD.target_id;
                END IF;
                RETURN OLD;
            ELSIF TG_OP = 'UPDATE' THEN
                -- Handle amount or endpoints change: reverse OLD then apply NEW
                PERFORM treasury_apply_transaction_rev(OLD);
                PERFORM treasury_apply_transaction_ins(NEW);
                RETURN NEW;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION treasury_apply_transaction_ins(rec treasury_transactions) RETURNS void AS $$
        DECLARE
            amt numeric := rec.amount;
        BEGIN
            IF rec.source_type = 'cash' THEN
                UPDATE cash_accounts SET balance = balance - amt WHERE id = rec.source_id;
            ELSE
                UPDATE bank_accounts SET balance = balance - amt WHERE id = rec.source_id;
            END IF;
            IF rec.target_type = 'cash' THEN
                UPDATE cash_accounts SET balance = balance + amt WHERE id = rec.target_id;
            ELSE
                UPDATE bank_accounts SET balance = balance + amt WHERE id = rec.target_id;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION treasury_apply_transaction_rev(rec treasury_transactions) RETURNS void AS $$
        DECLARE
            amt numeric := rec.amount;
        BEGIN
            IF rec.source_type = 'cash' THEN
                UPDATE cash_accounts SET balance = balance + amt WHERE id = rec.source_id;
            ELSE
                UPDATE bank_accounts SET balance = balance + amt WHERE id = rec.source_id;
            END IF;
            IF rec.target_type = 'cash' THEN
                UPDATE cash_accounts SET balance = balance - amt WHERE id = rec.target_id;
            ELSE
                UPDATE bank_accounts SET balance = balance - amt WHERE id = rec.target_id;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_treasury_tx_after_ins
        AFTER INSERT ON treasury_transactions
        FOR EACH ROW EXECUTE FUNCTION treasury_apply_transaction();
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_treasury_tx_after_del
        AFTER DELETE ON treasury_transactions
        FOR EACH ROW EXECUTE FUNCTION treasury_apply_transaction();
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_treasury_tx_after_upd
        AFTER UPDATE ON treasury_transactions
        FOR EACH ROW EXECUTE FUNCTION treasury_apply_transaction();
        """
    )


def downgrade():
    # drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_treasury_tx_after_upd ON treasury_transactions;")
    op.execute("DROP TRIGGER IF EXISTS trg_treasury_tx_after_del ON treasury_transactions;")
    op.execute("DROP TRIGGER IF EXISTS trg_treasury_tx_after_ins ON treasury_transactions;")

    # drop functions
    for fn in ['treasury_apply_transaction', 'treasury_apply_transaction_ins', 'treasury_apply_transaction_rev']:
        op.execute(f"DROP FUNCTION IF EXISTS {fn} CASCADE;")

    # drop tables
    op.drop_index('ix_bank_recon_bank_period', table_name='bank_reconciliations')
    op.drop_table('bank_reconciliations')

    op.drop_index('ix_treasury_transactions_date', table_name='treasury_transactions')
    op.drop_constraint('ck_treasury_tx_amount_positive', 'treasury_transactions', type_='check')
    op.drop_table('treasury_transactions')

    op.drop_index('ix_bank_accounts_account_number', table_name='bank_accounts')
    op.drop_table('bank_accounts')

    op.drop_index('ix_cash_accounts_code', table_name='cash_accounts')
    op.drop_table('cash_accounts')

    # drop enums
    recon_status = postgresql.ENUM(name='recon_status')
    recon_status.drop(op.get_bind(), checkfirst=True)
    source_type = postgresql.ENUM(name='source_type')
    source_type.drop(op.get_bind(), checkfirst=True)
