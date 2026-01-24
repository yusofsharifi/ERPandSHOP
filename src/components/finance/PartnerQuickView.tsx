import React, { useEffect, useState } from 'react'
import { Card, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'

export default function PartnerQuickView({ partnerId, onClose }: { partnerId: string; onClose: () => void }) {
  const { i18n } = useTranslation()
  const [summary, setSummary] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let mounted = true
    const fetchSummary = async () => {
      setLoading(true)
      try {
        const res = await fetch(`/api/v1/arap/partners/${partnerId}`)
        if (!res.ok) return
        const data = await res.json()
        if (mounted) setSummary(data)
      } catch (e) {
        // ignore
      } finally { if (mounted) setLoading(false) }
    }
    if (partnerId) fetchSummary()
    return () => { mounted = false }
  }, [partnerId])

  return (
    <Card className="w-80">
      <CardContent>
        <div className="flex justify-between items-center mb-3">
          <div className="font-semibold">{summary?.name || (i18n.language === 'fa' ? 'اطلاعات' : 'Partner')}</div>
          <Button variant="outline" onClick={onClose}>×</Button>
        </div>
        {loading && <div>Loading...</div>}
        {!loading && summary && (
          <div className="space-y-2 text-sm">
            <div>{i18n.language === 'fa' ? 'مانده' : 'Balance'}: {summary.balance_amount ?? '-'}</div>
            <div>{i18n.language === 'fa' ? 'تعداد فاکتورهای معوق' : 'Overdue'}: {summary.overdue_count ?? 0}</div>
            <div>{i18n.language === 'fa' ? 'فاکتورهای اخیر' : 'Recent Invoices'}:</div>
            <div className="space-y-1">
              {(summary.recent_invoices || []).slice(0,5).map((inv:any)=> (
                <div key={inv.id} className="text-xs">{inv.invoice_no} — {inv.balance_amount}</div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
