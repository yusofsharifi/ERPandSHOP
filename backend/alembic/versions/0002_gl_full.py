"""create full general ledger schema

Revision ID: 0002_gl_full
Revises: 
Create Date: 2025-10-20 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002_gl_full'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ensure pgcrypto for gen_random_uuid
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # enums
    account_type = postgresql.ENUM('asset','liability','equity','revenue','expense', name='account_type')
    account_type.create(op.get_bind(), checkfirst=True)

    journal_status = postgresql.ENUM('draft','posted','cancelled', name='journal_status')
    journal_status.create(op.get_bind(), checkfirst=True)

    # accounts
    op.create_table(
        'accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=128), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.Enum('asset','liability','equity','revenue','expense', name='account_type'), nullable=False),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('accounts.id', ondelete='SET NULL')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_accounts_code', 'accounts', ['code'])
    op.create_unique_constraint('uq_accounts_company_code', 'accounts', ['company_id','code'])

    # journal_entries
    op.create_table(
        'journal_entries',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('number', sa.String(length=64), nullable=True, unique=True),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('jalali_date', sa.String(length=32), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('total_debit', sa.Numeric(18,2), nullable=False),
        sa.Column('total_credit', sa.Numeric(18,2), nullable=False),
        sa.Column('status', sa.Enum('draft','posted','cancelled', name='journal_status'), nullable=False, server_default='draft'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_journal_entries_date', 'journal_entries', ['date'])
    op.create_index('ix_journal_entries_number', 'journal_entries', ['number'])
    op.create_check_constraint('ck_journal_total_debit_non_negative', 'journal_entries', 'total_debit >= 0')
    op.create_check_constraint('ck_journal_total_credit_non_negative', 'journal_entries', 'total_credit >= 0')

    # journal_lines
    op.create_table(
        'journal_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('journal_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('journal_entries.id', ondelete='CASCADE'), nullable=False),
        sa.Column('line_no', sa.Integer(), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('debit', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('credit', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
    )
    op.create_unique_constraint('uq_journal_lines_journal_line_no', 'journal_lines', ['journal_id','line_no'])
    op.create_check_constraint('ck_journal_line_debit_non_negative', 'journal_lines', 'debit >= 0')
    op.create_check_constraint('ck_journal_line_credit_non_negative', 'journal_lines', 'credit >= 0')

    # gl_auto_number
    op.create_table(
        'gl_auto_number',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('last_number', sa.BigInteger(), nullable=False, server_default='0'),
    )
    op.create_unique_constraint('uq_gl_auto_number_year_company', 'gl_auto_number', ['year','company_id'])

    # audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('ts', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_audit_entity', 'audit_logs', ['entity_type','entity_id'])


def downgrade():
    op.drop_index('ix_audit_entity', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_constraint('uq_gl_auto_number_year_company', 'gl_auto_number', type_='unique')
    op.drop_table('gl_auto_number')
    op.drop_constraint('uq_journal_lines_journal_line_no', 'journal_lines', type_='unique')
    op.drop_table('journal_lines')
    op.drop_constraint('ck_journal_total_credit_non_negative', 'journal_entries', type_='check')
    op.drop_constraint('ck_journal_total_debit_non_negative', 'journal_entries', type_='check')
    op.drop_index('ix_journal_entries_date', table_name='journal_entries')
    op.drop_index('ix_journal_entries_number', table_name='journal_entries')
    op.drop_table('journal_entries')
    op.drop_constraint('uq_accounts_company_code', 'accounts', type_='unique')
    op.drop_index('ix_accounts_code', table_name='accounts')
    op.drop_table('accounts')
    # drop enums
    journal_status = postgresql.ENUM(name='journal_status')
    journal_status.drop(op.get_bind(), checkfirst=True)
    account_type = postgresql.ENUM(name='account_type')
    account_type.drop(op.get_bind(), checkfirst=True)
