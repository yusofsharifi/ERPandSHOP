import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import InvoiceStatusBadge from '@/components/invoices/InvoiceStatusBadge'
import PaymentModal from '@/components/invoices/PaymentModal'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

const InvoiceDetail: React.FC = () => {
  const { id } = useParams()
  const { i18n } = useTranslation()
  const [inv, setInv] = useState<any | null>(null)
  const [tab, setTab] = useState('overview')
  const [openPay, setOpenPay] = useState(false)

  const fetchInvoice = async () => {
    if (!id) return
    try {
      const res = await fetch(`/api/v1/invoices/${id}`)
      if (!res.ok) { toast.error(i18n.language === 'fa' ? 'خطا' : 'Error'); return }
      const json = await res.json()
      setInv(json)
    } catch (e) { toast.error('Error') }
  }

  useEffect(()=> { fetchInvoice() }, [id])

  if (!inv) return <div>{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{i18n.language === 'fa' ? 'جزئیات فاکتور' : 'Invoice Detail'}</h2>
        <div className="flex gap-2 items-center">
          <InvoiceStatusBadge status={inv.status} />
          <Button onClick={()=> setOpenPay(true)}>{i18n.language === 'fa' ? 'ثبت پرداخت' : 'Record payment'}</Button>
        </div>
      </div>

      <div className="mb-4">
        <nav className="flex gap-2">
          <button onClick={()=> setTab('overview')} className={`px-3 py-1 ${tab==='overview' ? 'bg-gray-100' : ''}`}>{i18n.language === 'fa' ? 'نمای کلی' : 'Overview'}</button>
          <button onClick={()=> setTab('payments')} className={`px-3 py-1 ${tab==='payments' ? 'bg-gray-100' : ''}`}>{i18n.language === 'fa' ? 'پرداخت‌ها' : 'Payments'}</button>
          <button onClick={()=> setTab('journal')} className={`px-3 py-1 ${tab==='journal' ? 'bg-gray-100' : ''}`}>{i18n.language === 'fa' ? 'دفتر کل' : 'Journal Entry'}</button>
          <button onClick={()=> setTab('history')} className={`px-3 py-1 ${tab==='history' ? 'bg-gray-100' : ''}`}>{i18n.language === 'fa' ? 'تاریخچه' : 'History'}</button>
        </nav>
      </div>

      {tab === 'overview' && (
        <Card>
          <CardHeader>
            <CardTitle>{i18n.language === 'fa' ? 'مشخصات' : 'Overview'}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div><strong>{i18n.language === 'fa' ? 'شماره' : 'Invoice No'}:</strong> {inv.invoice_no || inv.id}</div>
                <div><strong>{i18n.language === 'fa' ? 'مشتری' : 'Customer'}:</strong> {inv.partner_id}</div>
                <div><strong>{i18n.language === 'fa' ? 'تاریخ' : 'Date'}:</strong> {inv.date}</div>
              </div>
              <div>
                <div><strong>{i18n.language === 'fa' ? 'جمع کل' : 'Total'}:</strong> {inv.total_amount}</div>
                <div><strong>{i18n.language === 'fa' ? 'وضعیت' : 'Status'}:</strong> <InvoiceStatusBadge status={inv.status} /></div>
              </div>
            </div>

            <div className="mt-4">
              <h4 className="font-medium mb-2">{i18n.language === 'fa' ? 'ردیف‌ها' : 'Lines'}</h4>
              <div className="space-y-2">
                {inv.lines && inv.lines.map((l:any)=> (
                  <div key={l.id} className="p-2 border rounded">
                    <div className="flex justify-between"><div>{l.description}</div><div>{l.line_total}</div></div>
                    <div className="text-sm text-muted-foreground">{l.qty} x {l.unit_price} (tax {l.tax_rate}%)</div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {tab === 'payments' && (
        <Card>
          <CardHeader>
            <CardTitle>{i18n.language === 'fa' ? 'پرداخت‌ها' : 'Payments'}</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Call legacy ARAP payments endpoint if available */}
            <PaymentsList invoiceId={id!} />
          </CardContent>
        </Card>
      )}

      {tab === 'journal' && (
        <Card>
          <CardHeader><CardTitle>{i18n.language === 'fa' ? 'دفتر کل' : 'Journal Entry'}</CardTitle></CardHeader>
          <CardContent>
            <div>{i18n.language==='fa' ? 'ورودی دفتر کل پس از ثبت فاکتور ایجاد می‌شود' : 'Journal entries created on posting will appear here'}</div>
          </CardContent>
        </Card>
      )}

      {tab === 'history' && (
        <Card>
          <CardHeader><CardTitle>{i18n.language === 'fa' ? 'تاریخچه' : 'History'}</CardTitle></CardHeader>
          <CardContent>
            <div>{i18n.language === 'fa' ? 'نمایش تاریخچه عملیات' : 'Audit and history events'}</div>
          </CardContent>
        </Card>
      )}

      <PaymentModal open={openPay} invoiceId={id || ''} partnerId={inv.partner_id} onClose={(saved)=> { setOpenPay(false); if (saved) fetchInvoice() }} />
    </div>
  )
}

const PaymentsList: React.FC<{ invoiceId: string }> = ({ invoiceId }) => {
  const [items, setItems] = useState<any[]>([])
  const { i18n } = useTranslation()
  useEffect(()=>{
    const fetch = async () => {
      try {
        const res = await fetch(`/api/v1/arap/invoices/${invoiceId}/payments`)
        if (!res.ok) { setItems([]); return }
        const data = await res.json()
        setItems(Array.isArray(data) ? data : (data.items || data))
      } catch (e) { setItems([]) }
    }
    fetch()
  }, [invoiceId])
  return (
    <div>
      {items.length === 0 && <div>{i18n.language === 'fa' ? 'پرداختی ثبت نشده' : 'No payments'}</div>}
      {items.map(p => (
        <div key={p.id} className="p-2 border rounded mb-2">
          <div className="flex justify-between"><div>{p.method}</div><div>{p.amount}</div></div>
          <div className="text-sm text-muted-foreground">{p.payment_date}</div>
        </div>
      ))}
    </div>
  )
}

export default InvoiceDetail
