from app.parsers.bank_parsers import parse_csv, parse_mt940, simple_match_suggestions


def test_parse_csv():
    csv = 'date,description,amount,currency,reference\n2021-01-01,Payment,100,USD,REF1\n'
    res = parse_csv(csv)
    assert len(res) == 1
    assert res[0]['amount'] == 100


def test_parse_mt940():
    mt = ':61:2101010101D1000,00NTRF\n:86:Payment from customer\n'
    res = parse_mt940(mt)
    assert isinstance(res, list)


def test_simple_match():
    bank = [{'statement_date':'2021-01-01','amount':100,'description':'Invoice 123'}]
    sys = [{'date':'2021-01-01','amount':100,'description':'Invoice 123'}]
    sug = simple_match_suggestions(bank, sys)
    assert len(sug) > 0
