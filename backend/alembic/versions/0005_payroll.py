"""
create payroll schema: employees, salary_structures, payroll_runs, payroll_lines, payroll_journal_links

Revision ID: 0005_payroll
Revises: 0004_treasury
Create Date: 2025-10-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0005_payroll'
down_revision = '0004_treasury'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    payroll_status = postgresql.ENUM('draft','computed','posted', name='payroll_status')
    payroll_status.create(op.get_bind(), checkfirst=True)

    # employees
    op.create_table(
        'employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('national_id', sa.String(length=64), nullable=True),
        sa.Column('employment_no', sa.String(length=64), nullable=True),
        sa.Column('bank_account', sa.String(length=128), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('tax_code', sa.String(length=64), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_employees_national_id', 'employees', ['national_id'])
    op.create_unique_constraint('uq_employees_employment_no', 'employees', ['employment_no'])

    # salary_structures
    op.create_table(
        'salary_structures',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('base_salary', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('allowances', postgresql.JSONB(), nullable=True),
        sa.Column('deductions', postgresql.JSONB(), nullable=True),
        sa.Column('taxable', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # payroll_runs
    op.create_table(
        'payroll_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.Enum('draft','computed','posted', name='payroll_status'), nullable=False, server_default='draft'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_payroll_runs_period', 'payroll_runs', ['period_start','period_end'])

    # payroll_lines
    op.create_table(
        'payroll_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('payroll_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payroll_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('gross', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('taxes', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('deductions', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('net', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('components', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_check_constraint('ck_payroll_line_gross_non_negative', 'payroll_lines', 'gross >= 0')
    op.create_check_constraint('ck_payroll_line_net_non_negative', 'payroll_lines', 'net >= 0')
    op.create_unique_constraint('uq_payroll_line_employee_period', 'payroll_lines', ['employee_id','period_start','period_end'])

    # payroll_journal_links
    op.create_table(
        'payroll_journal_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('payroll_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('payroll_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('journal_entries.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_payroll_journal_run', 'payroll_journal_links', ['payroll_run_id'])


def downgrade():
    op.drop_index('ix_payroll_journal_run', table_name='payroll_journal_links')
    op.drop_table('payroll_journal_links')

    op.drop_constraint('uq_payroll_line_employee_period', 'payroll_lines', type_='unique')
    op.drop_constraint('ck_payroll_line_net_non_negative', 'payroll_lines', type_='check')
    op.drop_constraint('ck_payroll_line_gross_non_negative', 'payroll_lines', type_='check')
    op.drop_table('payroll_lines')

    op.drop_index('ix_payroll_runs_period', table_name='payroll_runs')
    op.drop_table('payroll_runs')

    op.drop_table('salary_structures')

    op.drop_constraint('uq_employees_employment_no', 'employees', type_='unique')
    op.drop_index('ix_employees_national_id', table_name='employees')
    op.drop_table('employees')

    payroll_status = postgresql.ENUM(name='payroll_status')
    payroll_status.drop(op.get_bind(), checkfirst=True)
