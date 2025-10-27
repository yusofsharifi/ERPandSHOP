import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import SimpleChart from '@/components/ui/SimpleChart'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'

const bucketsLabels = ['0', '1-30', '31-60', '61-90', '90+']

const PartnerAgingPage: React.FC = () => {
  const { id } = useParams()
  const { i18n } = useTranslation()
  const [data, setData] = useState<number[]>([0,0,0,0,0])
  const [invoices, setInvoices] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(()=>{
    const fetchAging = async () => {
      setLoading(true)
      try {
        const res = await fetch(`/api/v1/arap/partners/${id}/aging`)
        if (!res.ok) return
        const json = await res.json()
        setData([json.bucket_0 || 0, json.bucket_30 || 0, json.bucket_60 || 0, json.bucket_90 || 0, json.bucket_90_plus || 0])
        setInvoices(json.invoices || [])
      } catch (e) {
        // ignore
      } finally { setLoading(false) }
    }
    if (id) fetchAging()
  }, [id])

  const exportCsv = async () => {
    const res = await fetch(`/api/v1/arap/partners/${id}/aging/export`)
    if (!res.ok) return
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `aging_${id}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{i18n.language === 'fa' ? 'گزارش Aging' : 'Aging Report'}</h2>
        <div />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{i18n.language === 'fa' ? 'Aging' : 'Aging'}</CardTitle>
        </CardHeader>
        <CardContent>
          {loading && <div>{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>}
          {!loading && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <SimpleChart data={data} />
                <div className="mt-2 grid grid-cols-5 gap-2 text-sm">
                  {bucketsLabels.map((l,i)=> (
                    <div key={i} className="p-2 border rounded text-center">{l}<div className="font-semibold">{data[i]}</div></div>
                  ))}
                </div>
              </div>
              <div>
                <div className="flex justify-between items-center mb-2">
                  <div className="font-semibold">{i18n.language === 'fa' ? 'فاکتورهای مرتبط' : 'Linked Invoices'}</div>
                  <Button onClick={exportCsv}>{i18n.language === 'fa' ? 'صادرات' : 'Export'}</Button>
                </div>
                <div className="space-y-2">
                  {invoices.map(inv => (
                    <div key={inv.id} className="p-2 border rounded">{inv.invoice_no} — {inv.balance_amount}</div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default PartnerAgingPage
