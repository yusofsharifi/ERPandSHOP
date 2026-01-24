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
    """Improved MT940 parser handling multiple :61: and :86: blocks.
    Returns list of dicts with statement_date (ISO), amount (float), description, reference
    """
    lines = content.splitlines()
    txns = []
    curr = None
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith(':61:'):
            # capture basic parts
            # format :61:YYMMDD[MMDD]C/Damount...optional
            m = re.match(r':61:(\d{6})(?:\d{4})?([CD])(\d+[\d,\.]*)', line)
            if m:
                yymmdd = m.group(1)
                sign = m.group(2)
                amt = m.group(3).replace(',', '.')
                try:
                    # convert YYMMDD to YYYY-MM-DD (approximate 20xx)
                    yy = int(yymmdd[0:2])
                    year = 2000 + yy if yy < 80 else 1900 + yy
                    month = int(yymmdd[2:4])
                    day = int(yymmdd[4:6])
                    date_iso = f"{year:04d}-{month:02d}-{day:02d}"
                except Exception:
                    date_iso = None
                try:
                    amt_f = float(amt)
                    if sign == 'D':
                        amt_f = -amt_f
                except Exception:
                    amt_f = 0.0
                curr = {'statement_date': date_iso, 'amount': amt_f, 'description': '', 'reference': ''}
                txns.append(curr)
        elif line.startswith(':86:') and curr is not None:
            # narrative may span multiple lines until next tag
            desc = line[4:]
            # consume following lines that are not new tags
            j = i+1
            while j < len(lines) and not re.match(r'^:\d{2}:', lines[j].strip()):
                desc += ' ' + lines[j].strip()
                j += 1
            curr['description'] = desc
        else:
            # ignore other lines
            continue
    return txns


def detect_statement_format(content: str) -> str:
    """Return 'mt940' or 'csv' or 'unknown'"""
    if ':61:' in content or ':86:' in content:
        return 'mt940'
    # simple CSV detection
    first = content.strip().splitlines()[0] if content.strip() else ''
    if ',' in first and any(h in first.lower() for h in ['date','amount','description']):
        return 'csv'
    return 'unknown'


def parse_statement(content: str):
    fmt = detect_statement_format(content)
    if fmt == 'mt940':
        return parse_mt940(content)
    if fmt == 'csv':
        return parse_csv(content)
    # fallback to csv parse attempt
    return parse_csv(content)


from difflib import SequenceMatcher

def simple_match_suggestions(bank_lines: List[Dict], system_txns: List[Dict]) -> List[Dict]:
    """Return list of suggestions with heuristics: amount match, date proximity, reference, and fuzzy description match."""
    suggestions = []
    for b in bank_lines:
        for s in system_txns:
            score = 0.0
            try:
                # amount exact or near
                amt_b = float(b.get('amount',0))
                amt_s = float(s.get('amount',0))
                if abs(amt_b - amt_s) < 0.001:
                    score += 0.5
                elif abs(amt_b - amt_s) / max(abs(amt_s),1) < 0.01:
                    score += 0.3

                # reference exact match
                if b.get('reference') and s.get('reference') and str(b.get('reference')).strip() == str(s.get('reference')).strip():
                    score += 0.6

                # date proximity: exact day or within 1 day
                bd = str(b.get('statement_date',''))
                sd = str(s.get('date',''))
                if bd and sd and bd == sd:
                    score += 0.3
                elif bd and sd and bd[:10] == sd[:10]:
                    score += 0.2

                # fuzzy description similarity
                b_desc = str(b.get('description','')).lower()
                s_desc = str(s.get('description','') or s.get('reference','')).lower()
                if b_desc and s_desc:
                    ratio = SequenceMatcher(None, b_desc, s_desc).ratio()
                    score += min(0.4, ratio * 0.4)
            except Exception:
                pass
            if score > 0:
                suggestions.append({'line': b, 'txn': s, 'score': round(score,2)})
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    return suggestions
