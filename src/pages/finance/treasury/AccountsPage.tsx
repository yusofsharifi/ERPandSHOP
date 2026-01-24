import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import SimpleChart from '@/components/ui/SimpleChart'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

const AccountsPage: React.FC = () => {
  const { t, i18n } = useTranslation()
  const [accounts, setAccounts] = useState<any[]>([])
  const [q, setQ] = useState('')
  const [type, setType] = useState<string | ''>('')

  const fetchList = async () => {
    try {
      const params = new URLSearchParams()
      if (type) params.set('type', type)
      const res = await fetch('/api/treasury/accounts?' + params.toString())
      if (!res.ok) throw new Error('Failed')
      const data = await res.json()
      setAccounts(Array.isArray(data) ? data : [])
    } catch (e) {
      console.error(e)
      toast.error(t('error') || 'Error')
    }
  }

  useEffect(() => { fetchList() }, [type])

  const filtered = accounts.filter(a => !q || (a.name || '').toLowerCase().includes(q.toLowerCase()) || (a.code||'').toLowerCase().includes(q.toLowerCase()))

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('treasury.accounts')}</h2>
        <div className="flex gap-2">
          <Button onClick={fetchList}>{t('refresh') || 'Refresh'}</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('treasury.accounts')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input placeholder={t('search') || 'Search...'} value={q} onChange={(e:any)=> setQ(e.target.value)} />
            <select value={type} onChange={(e)=> setType(e.target.value)} className="p-2 border rounded">
              <option value="">All</option>
              <option value="cash">{t('treasury.cash_accounts')}</option>
              <option value="bank">{t('treasury.bank_accounts')}</option>
            </select>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left">
                  <th className="px-2 py-1">Code</th>
                  <th className="px-2 py-1">Name</th>
                  <th className="px-2 py-1">Currency</th>
                  <th className="px-2 py-1">Balance</th>
                  <th className="px-2 py-1">Activity</th>
                  <th className="px-2 py-1">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(acc => (
                  <tr key={acc.id} className="border-t">
                    <td className="px-2 py-2">{acc.code || acc.account_number || '-'}</td>
                    <td className="px-2 py-2">{acc.name || acc.bank_name}</td>
                    <td className="px-2 py-2">{acc.currency}</td>
                    <td className={"px-2 py-2 " + (acc.balance < 0 ? 'text-red-600' : acc.balance < 100 ? 'text-yellow-600' : 'text-green-600')}>{Number(acc.balance || 0).toFixed(2)}</td>
                    <td className="px-2 py-2 w-36"><SimpleChart data={[(acc.balance||0)/10, (acc.balance||0)/8, (acc.balance||0)/6, (acc.balance||0)/4, (acc.balance||0)/2]} /></td>
                    <td className="px-2 py-2">
                      <div className="flex gap-2">
                        <a className="underline text-primary" href={`/finance/treasury/accounts/${acc.id}/ledger`}>{t('ledger') || 'Ledger'}</a>
                        <a className="underline text-primary" href={`/finance/treasury/transfer?from_id=${acc.id}`}>{t('treasury.transfer')}</a>
                        <Button size="sm" variant="outline">{t('treasury.recharge') || 'Recharge'}</Button>
                      </div>
                    </td>
                  </tr>
                ))}
                {filtered.length === 0 && <tr><td colSpan={6} className="p-4 text-center text-sm text-muted">No accounts</td></tr>}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default AccountsPage
