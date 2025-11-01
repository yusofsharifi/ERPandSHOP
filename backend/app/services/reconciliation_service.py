from typing import List, Dict, Any
from app.parsers.bank_parsers import simple_match_suggestions
from app.db.session import SessionLocal
from app.models.treasury import BankStatementLine, TreasuryTransaction, BankReconciliation, AuditLog
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID


def create_reconciliation_from_lines(db: Session, company_id: UUID, bank_account_id: UUID, lines: List[Dict[str,Any]], created_by: UUID = None) -> BankReconciliation:
    recon = BankReconciliation(company_id=company_id, bank_account_id=bank_account_id, period_start=lines[0].get('statement_date'), period_end=lines[-1].get('statement_date'), reconciliation_data={'imported': len(lines)}, created_by=created_by)
    db.add(recon)
    db.flush()
    for l in lines:
        bsl = BankStatementLine(reconciliation_id=recon.id, bank_account_id=bank_account_id, statement_date=l.get('statement_date'), description=l.get('description'), amount=l.get('amount'), currency=l.get('currency','USD'), reference=l.get('reference'))
        db.add(bsl)
    db.commit()
    db.refresh(recon)
    return recon


def suggest_matches(db: Session, reconciliation_id: UUID) -> List[Dict]:
    # load bank lines and recent treasury txns
    recon = db.query(BankReconciliation).filter(BankReconciliation.id == reconciliation_id).first()
    if not recon:
        return []
    bank_lines = db.query(BankStatementLine).filter(BankStatementLine.reconciliation_id == reconciliation_id).all()
    # simple system txns within period
    sys_txns = db.query(TreasuryTransaction).filter(TreasuryTransaction.company_id == recon.company_id, TreasuryTransaction.date >= recon.period_start, TreasuryTransaction.date <= recon.period_end).all()
    # convert to dicts
    bl = [{'id': str(b.id), 'statement_date': getattr(b,'statement_date',None), 'description': getattr(b,'description',None), 'amount': float(getattr(b,'amount',0)), 'currency': getattr(b,'currency',None), 'reference': getattr(b,'reference',None)} for b in bank_lines]
    st = [{'id': str(s.id), 'date': getattr(s,'date',None), 'description': getattr(s,'reference',None), 'amount': float(getattr(s,'amount',0)), 'currency': getattr(s,'currency',None)} for s in sys_txns]
    suggestions = simple_match_suggestions(bl, st)
    return suggestions


def apply_reconciliation(db: Session, reconciliation_id: UUID, applied_by: UUID = None):
    recon = db.query(BankReconciliation).filter(BankReconciliation.id == reconciliation_id).with_for_update().first()
    if not recon:
        raise KeyError('reconciliation_not_found')
    # mark matched lines and create transactions for unmatched
    bank_lines = db.query(BankStatementLine).filter(BankStatementLine.reconciliation_id == reconciliation_id).all()
    created = []
    for b in bank_lines:
        if not b.matched:
            # create treasury transaction from bank to system cash with amount
            txn = TreasuryTransaction(company_id=recon.company_id, source_type='bank', source_id=recon.bank_account_id, target_type='cash', target_id=None, amount=b.amount, currency=b.currency, exchange_rate=1, date=datetime.utcnow(), reference=f'recon:{reconciliation_id}:{b.id}', posted=False)
            db.add(txn)
            db.flush()
            created.append(txn.id)
            b.matched = True
            db.add(b)
    recon.status = 'applied'
    recon.applied_by = applied_by
    recon.applied_at = datetime.utcnow()
    db.add(recon)
    db.commit()
    # audit
    al = AuditLog(company_id=recon.company_id, actor_id=applied_by, action='treasury.reconciliation.apply', object_type='bank_reconciliation', object_id=recon.id, payload={'created_txns': [str(c) for c in created]})
    db.add(al)
    db.commit()
    return {'created': created}
