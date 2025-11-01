import csv
from typing import List, Dict
from io import StringIO


def parse_csv(content: str) -> List[Dict]:
    """Parse simple bank CSV with headers: date,description,amount,currency,reference"""
    f = StringIO(content)
    reader = csv.DictReader(f)
    out = []
    for r in reader:
        try:
            out.append({
                'statement_date': r.get('date') or r.get('statement_date'),
                'description': r.get('description') or r.get('desc'),
                'amount': float(r.get('amount') or r.get('credit') or 0),
                'currency': r.get('currency') or 'USD',
                'reference': r.get('reference') or r.get('ref')
            })
        except Exception:
            continue
    return out


def parse_mt940(content: str) -> List[Dict]:
    # very small skeleton parser returning empty list
    # full MT940 parsing is out of scope for this generator
    return []
