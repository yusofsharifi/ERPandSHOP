import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

const TransactionList: React.FC<{ customerId: string }> = ({ customerId }) => {
  const { i18n } = useTranslation()
  const [data, setData] = useState<any | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchTx = async () => {
    if (!customerId) return
    setLoading(true)
    try {
      const res = await fetch(`/api/v1/customers/${customerId}/transactions`)
      if (!res.ok) { setData(null); return }
      const json = await res.json()
      setData(json)
    } catch (e) {
      setData(null)
    } finally { setLoading(false) }
  }

  useEffect(() => { fetchTx() }, [customerId])

  return (
    <Card>
      <CardHeader>
        <CardTitle>{i18n.language==='fa' ? 'تراکنش‌ها' : 'Transactions'}</CardTitle>
      </CardHeader>
      <CardContent>
        {loading && <div>{i18n.language==='fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>}
        {!loading && data && (
          <div>
            <div className="mb-2"><strong>{i18n.language==='fa' ? 'مانده' : 'Balance'}:</strong> {data.balance}</div>
            <div>
              {Array.isArray(data.transactions) ? data.transactions.map((t:any) => (
                <div key={t.id || Math.random()} className="border rounded p-2 mb-2">
                  <div className="text-sm text-muted-foreground">{t.type}</div>
                  <div className="mt-1">{t.amount}</div>
                </div>
              )) : <div>{i18n.language==='fa' ? 'موردی نیست' : 'No transactions'}</div>}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default TransactionList
