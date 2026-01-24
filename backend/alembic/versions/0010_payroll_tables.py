"""create payroll tables

Revision ID: 0010_payroll_tables
Revises: 0009_treasury_tables
Create Date: 2025-11-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0010_payroll_tables'
down_revision = '0009_treasury_tables'
branch_labels = None
depends_on = None


def upgrade():
    # Enums
    op.execute("CREATE TYPE contract_type AS ENUM ('permanent','contract','part_time','hourly');")
    op.execute("CREATE TYPE payroll_status AS ENUM ('draft','validated','closed');")
    op.execute("CREATE TYPE payment_status AS ENUM ('unpaid','in_progress','paid');")
    op.execute("CREATE TYPE payroll_line_type AS ENUM ('earning','deduction');")

    # employees
    op.create_table(
        'employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_code', sa.String(length=64), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=False),
        sa.Column('last_name', sa.String(length=255), nullable=False),
        sa.Column('national_id', sa.String(length=64), nullable=True),
        sa.Column('job_title', sa.String(length=255), nullable=True),
        sa.Column('department_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=True),
        sa.Column('contract_type', postgresql.ENUM('permanent','contract','part_time','hourly', name='contract_type'), nullable=False),
        sa.Column('base_salary', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('bank_account', sa.String(length=128), nullable=True),
        sa.Column('iban', sa.String(length=64), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_employees_national_id', 'employees', ['national_id'])
    op.create_unique_constraint('uq_employees_employee_code', 'employees', ['employee_code'])

    # salary_structures
    op.create_table(
        'salary_structures',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='IRR'),
        sa.Column('rules', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )

    # payroll_periods
    op.create_table(
        'payroll_periods',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', postgresql.ENUM('draft','validated','closed', name='payroll_status'), nullable=False, server_default='draft'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_payroll_periods_company_start_end', 'payroll_periods', ['company_id', 'start_date', 'end_date'])

    # payrolls
    op.create_table(
        'payrolls',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('period_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('structure_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('gross_salary', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('total_deductions', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('net_salary', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('payment_status', postgresql.ENUM('unpaid','in_progress','paid', name='payment_status'), nullable=False, server_default='unpaid'),
        sa.Column('journal_entry_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('pay_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_payrolls_employee_period_status', 'payrolls', ['employee_id', 'period_id', 'payment_status'])
    op.create_unique_constraint('uq_payroll_employee_period', 'payrolls', ['employee_id', 'period_id'])

    # payroll_lines
    op.create_table(
        'payroll_lines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('payroll_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', postgresql.ENUM('earning','deduction', name='payroll_line_type'), nullable=False),
        sa.Column('amount', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('formula', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_payroll_lines_payroll', 'payroll_lines', ['payroll_id'])

    # deductions
    op.create_table(
        'deductions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('payroll_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('amount', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_deductions_payroll', 'deductions', ['payroll_id'])

    # bonuses
    op.create_table(
        'bonuses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('payroll_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(length=64), nullable=False),
        sa.Column('amount', sa.Numeric(18,2), nullable=False, server_default='0'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_bonuses_payroll', 'bonuses', ['payroll_id'])


def downgrade():
    op.drop_index('ix_bonuses_payroll', table_name='bonuses')
    op.drop_table('bonuses')
    op.drop_index('ix_deductions_payroll', table_name='deductions')
    op.drop_table('deductions')
    op.drop_index('ix_payroll_lines_payroll', table_name='payroll_lines')
    op.drop_table('payroll_lines')
    op.drop_index('ix_payrolls_employee_period_status', table_name='payrolls')
    op.drop_table('payrolls')
    op.drop_index('ix_payroll_periods_company_start_end', table_name='payroll_periods')
    op.drop_table('payroll_periods')
    op.drop_table('salary_structures')
    op.drop_index('ix_employees_national_id', table_name='employees')
    op.drop_constraint('uq_employees_employee_code', 'employees', type_='unique')
    op.drop_table('employees')

    op.execute("DROP TYPE payroll_line_type;")
    op.execute("DROP TYPE payment_status;")
    op.execute("DROP TYPE payroll_status;")
    op.execute("DROP TYPE contract_type;")
