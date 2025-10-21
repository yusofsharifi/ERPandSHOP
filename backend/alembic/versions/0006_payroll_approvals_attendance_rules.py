"""
add payroll approvals flags, attendance_records and payroll_rules

Revision ID: 0006_payroll_approvals
Revises: 0005_payroll
Create Date: 2025-10-21 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0006_payroll_approvals'
down_revision = '0005_payroll'
branch_labels = None
depends_on = None


def upgrade():
    # add columns to payroll_runs
    op.add_column('payroll_runs', sa.Column('manager_approved', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    op.add_column('payroll_runs', sa.Column('manager_approved_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('payroll_runs', sa.Column('manager_approved_at', sa.DateTime(timezone=True), nullable=True))

    # attendance_records
    op.create_table(
        'attendance_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('hours_worked', sa.Numeric(10,2), nullable=True, server_default='0'),
        sa.Column('absence_days', sa.Numeric(10,2), nullable=True, server_default='0'),
        sa.Column('overtime_hours', sa.Numeric(10,2), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_attendance_employee_date', 'attendance_records', ['employee_id','date'])

    # payroll_rules
    op.create_table(
        'payroll_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('expression', sa.String(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('ix_payroll_rules_type', 'payroll_rules', ['rule_type'])


def downgrade():
    op.drop_index('ix_payroll_rules_type', table_name='payroll_rules')
    op.drop_table('payroll_rules')

    op.drop_index('ix_attendance_employee_date', table_name='attendance_records')
    op.drop_table('attendance_records')

    op.drop_column('payroll_runs', 'manager_approved_at')
    op.drop_column('payroll_runs', 'manager_approved_by')
    op.drop_column('payroll_runs', 'manager_approved')
