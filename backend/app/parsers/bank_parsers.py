import csv
from typing import List, Dict
from io import StringIO
import re


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
    """Very small MT940 skeleton parser. Extracts transactions from :61: tags and narrative from :86:"""
    lines = content.splitlines()
    txns = []
    curr = {}
    for i, line in enumerate(lines):
        if line.startswith(':61:'):
            # example: :61:1901010101D1000,00NTRFNONREF
            m = re.match(r':61:(\d{6})(\d{4})?([CD])([0-9,\.]+)', line)
            if m:
                date = m.group(1)
                sign = m.group(3)
                amt = m.group(4).replace(',', '.')
                amt_f = float(amt)
                if sign == 'D':
                    amt_f = -amt_f
                curr = {'statement_date': date, 'amount': amt_f, 'description': '', 'reference': ''}
                # look ahead for :86:
                if i+1 < len(lines) and lines[i+1].startswith(':86:'):
                    curr['description'] = lines[i+1][4:]
                txns.append(curr)
        # else ignore
    return txns


def simple_match_suggestions(bank_lines: List[Dict], system_txns: List[Dict]) -> List[Dict]:
    """Return list of suggestions with simple heuristics: amount exact match and date proximity.
    Score: 1.0 exact amount/date, 0.7 amount/date within 1 day, 0.5 description token overlap
    """
    suggestions = []
    for b in bank_lines:
        best = None
        for s in system_txns:
            score = 0.0
            try:
                if abs(float(b.get('amount',0)) - float(s.get('amount',0))) < 0.001:
                    score += 0.6
                # date proximity (if dates in YYYYMMDD or ISO)
                bd = str(b.get('statement_date',''))
                sd = str(s.get('date',''))
                if bd and sd and bd[:6] == sd[:6]:
                    score += 0.4
                # description token overlap
                b_tokens = set(str(b.get('description','')).lower().split())
                s_tokens = set(str(s.get('description','')).lower().split())
                if b_tokens and s_tokens:
                    overlap = len(b_tokens & s_tokens)
                    if overlap > 0:
                        score += min(0.3, overlap / max(len(b_tokens),1) * 0.3)
            except Exception:
                pass
            if score > 0:
                cand = {'line': b, 'txn': s, 'score': round(score,2)}
                suggestions.append(cand)
    # sort by score desc
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    return suggestions
