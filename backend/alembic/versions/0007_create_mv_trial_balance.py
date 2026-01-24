"""
create mv_trial_balance
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0007_create_mv_trial_balance'
down_revision = '0006_payroll_approvals_attendance_rules'
branch_labels = None
depends_on = None


def upgrade():
    # Create materialized view for trial balance
    op.execute("""
    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_trial_balance AS
    SELECT
      a.id as account_id,
      a.code as account_code,
      a.name as account_name,
      a.type as account_type,
      COALESCE(SUM(jl.debit),0) as total_debit,
      COALESCE(SUM(jl.credit),0) as total_credit,
      COALESCE(SUM(jl.debit) - SUM(jl.credit),0) as balance
    FROM accounts a
    LEFT JOIN journal_lines jl ON jl.account_id = a.id
    LEFT JOIN journal_entries je ON je.id = jl.journal_id AND je.status = 'posted'
    GROUP BY a.id, a.code, a.name, a.type;
    """)


def downgrade():
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_trial_balance;")
