import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'

type CashAccount = { id: string; name: string; code?: string; balance: string; currency: string }
type BankAccount = { id: string; bank_name: string; account_number: string; balance: string; currency: string }

const AccountsPage: React.FC = () => {
  const { i18n, t } = useTranslation()
  const [cash, setCash] = useState<CashAccount[]>([])
  const [banks, setBanks] = useState<BankAccount[]>([])

  const fetchData = async () => {
    try {
      const res1 = await fetch('/api/v1/treasury/cash_accounts')
      const res2 = await fetch('/api/v1/treasury/bank_accounts')
      const c = res1.ok ? await res1.json() : []
      const b = res2.ok ? await res2.json() : []
      setCash(c.items || c || [])
      setBanks(b.items || b || [])
    } catch (e) {
      // ignore
    }
  }

  useEffect(() => { fetchData() }, [])

  const lowBalance = (bal: string) => {
    try { return parseFloat(bal) < 0 }
    catch { return false }
  }

  return (
    <div dir={i18n.language === 'fa' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('treasury.accounts') || 'Treasury Accounts'}</h2>
        <div />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>{t('treasury.cash_accounts') || 'Cash Accounts'}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {cash.length === 0 && <div className="text-sm text-muted-foreground">No cash accounts</div>}
              {cash.map(c => (
                <div key={c.id} className={`p-3 border rounded flex items-center justify-between ${lowBalance(c.balance) ? 'bg-red-50' : ''}`}>
                  <div>
                    <div className="font-medium">{c.name}</div>
                    <div className="text-sm text-muted-foreground">{c.code || '-'}</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-semibold ${lowBalance(c.balance) ? 'text-destructive' : ''}`}>{c.balance} {c.currency}</div>
                    {lowBalance(c.balance) && <div className="text-xs text-destructive">{t('treasury.low_balance') || 'Low balance'}</div>}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('treasury.bank_accounts') || 'Bank Accounts'}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {banks.length === 0 && <div className="text-sm text-muted-foreground">No bank accounts</div>}
              {banks.map(b => (
                <div key={b.id} className={`p-3 border rounded flex items-center justify-between ${lowBalance(b.balance) ? 'bg-red-50' : ''}`}>
                  <div>
                    <div className="font-medium">{b.bank_name}</div>
                    <div className="text-sm text-muted-foreground">{b.account_number}</div>
                  </div>
                  <div className="text-right">
                    <div className={`font-semibold ${lowBalance(b.balance) ? 'text-destructive' : ''}`}>{b.balance} {b.currency}</div>
                    {lowBalance(b.balance) && <div className="text-xs text-destructive">{t('Low balance') || 'Low balance'}</div>}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default AccountsPage
