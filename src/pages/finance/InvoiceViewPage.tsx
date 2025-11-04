import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import { useParams, useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

const InvoiceViewPage: React.FC = () => {
  const { id } = useParams()
  const [inv, setInv] = useState<any>(null)
  const [payments, setPayments] = useState<any[]>([])
  const [openPay, setOpenPay] = useState(false)
  const navigate = useNavigate()
  const { i18n, t } = useTranslation()

  const fetchInv = async () => {
    try {
      const res = await fetch('/api/v1/arap/invoices')
      if (!res.ok) return
      const list = await res.json()
      const found = list.find((i: any) => i.id === id)
      setInv(found)
    } catch (e) {
      console.error(e)
    }
  }
  const fetchPayments = async () => {
    try {
      const res = await fetch(`/api/v1/arap/invoices/${id}/payments`)
      if (!res.ok) return setPayments([])
      const data = await res.json()
      setPayments(data)
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => { fetchInv(); fetchPayments() }, [id])
  const post = async () => {
    try {
      const r = await fetch(`/api/v1/arap/invoices/${id}/post`, { method: 'POST' })
      if (!r.ok) throw new Error('failed')
      toast.success(i18n.language === 'fa' ? 'فاکتور ثبت شد' : 'Invoice posted')
      fetchInv()
    } catch (e) {
      console.error(e)
      toast.error(i18n.language === 'fa' ? 'خطا در ثبت' : 'Post failed')
    }
  }
  const openPdf = () => {
    window.open(`/api/v1/arap/invoices/${id}/pdf`, '_blank')
  }

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('invoice') || (i18n.language === 'fa' ? 'فاکتور' : 'Invoice')}</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{i18n.language === 'fa' ? 'جزئیات فاکتور' : 'Invoice Details'}</CardTitle>
        </CardHeader>
        <CardContent>
          {!inv && <div>{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>}
          {inv && (
            <div>
              <div className="mb-2">{i18n.language === 'fa' ? 'شماره' : 'Number'}: {inv.invoice_no}</div>
              <div className="mb-2">{i18n.language === 'fa' ? 'تاریخ' : 'Date'}: {inv.date}</div>
              <div className="mb-2">{i18n.language === 'fa' ? 'وضعیت' : 'Status'}: {inv.status}</div>
              <div className="mb-4">{i18n.language === 'fa' ? 'جمع' : 'Total'}: {inv.total_amount} — {i18n.language === 'fa' ? 'مانده' : 'Balance'}: {inv.balance_amount}</div>
              <h4 className="font-semibold mb-2">{i18n.language === 'fa' ? 'سطرها' : 'Lines'}</h4>
              <div className="space-y-2">
                {inv.lines.map((l: any) => (
                  <div key={l.id} className="p-2 border rounded">{l.description} — {l.line_total}</div>
                ))}
              </div>

              <h4 className="font-semibold mt-4 mb-2">{i18n.language === 'fa' ? 'پرداخت‌ها' : 'Payments'}</h4>
              <div className="space-y-2">
                {payments.map(p => (
                  <div key={p.id} className="p-2 border rounded">{p.payment_date} — {p.amount} — {p.method}</div>
                ))}
                {payments.length === 0 && <div className="text-sm text-muted">{i18n.language === 'fa' ? 'پرداختی ثبت نشده' : 'No payments recorded'}</div>}
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter>
          <div className="flex gap-2 ml-auto">
            <Button onClick={() => setOpenPay(true)}>{i18n.language === 'fa' ? 'ثبت پرداخت' : 'Register Payment'}</Button>
            <Button onClick={openPdf} variant="outline">{i18n.language === 'fa' ? 'چاپ' : 'Print'}</Button>
            <Button onClick={post}>{i18n.language === 'fa' ? 'ثبت' : 'Post'}</Button>
          </div>
        </CardFooter>
      </Card>

      <Modal open={openPay} onOpenChange={setOpenPay} title={i18n.language === 'fa' ? 'ثبت پرداخت' : 'Register Payment'}>
        <PaymentForm invoice={inv} onSaved={() => { setOpenPay(false); fetchPayments(); fetchInv(); toast.success(i18n.language === 'fa' ? 'پرداخت ثبت شد' : 'Payment recorded') }} />
      </Modal>
    </div>
  )
}

function PaymentForm({ invoice, onSaved }: { invoice: any, onSaved?: () => void }){
  const { i18n } = useTranslation()
  const [amount, setAmount] = useState('')
  const [method, setMethod] = useState('cash')
  const [date, setDate] = useState(new Date().toISOString().slice(0,10))
  const [reference, setReference] = useState('')

  const submit = async () => {
    if (!invoice) return
    const rem = Number(invoice.balance_amount || invoice.total_amount || 0)
    const a = Number(amount || 0)
    if (a <= 0) return alert(i18n.language === 'fa' ? 'مبلغ باید بزرگتر از صفر باشد' : 'Amount must be > 0')
    if (a > rem) return alert(i18n.language === 'fa' ? 'مبلغ پرداخت بیشتر از مانده است' : 'Payment exceeds remaining balance')
    try {
      const payload = { partner_id: invoice.partner_id, invoice_id: invoice.id, amount: a, method, payment_date: date, reference }
      const res = await fetch('/api/v1/arap/payments', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (!res.ok) throw new Error('failed')
      onSaved && onSaved()
    } catch (e) {
      console.error(e)
      alert(i18n.language === 'fa' ? 'ثبت پرداخت ناموفق' : 'Failed to record payment')
    }
  }

  return (
    <div className="space-y-3">
      <div>
        <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'مبلغ' : 'Amount'}</label>
        <Input type="number" value={amount} onChange={(e:any)=> setAmount(e.target.value)} />
      </div>
      <div>
        <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'روش' : 'Method'}</label>
        <select value={method} onChange={(e)=> setMethod(e.target.value)} className="p-2 border rounded">
          <option value="cash">{i18n.language === 'fa' ? 'نقد' : 'Cash'}</option>
          <option value="bank">{i18n.language === 'fa' ? 'بانک' : 'Bank'}</option>
          <option value="check">{i18n.language === 'fa' ? 'چک' : 'Check'}</option>
        </select>
      </div>
      <div>
        <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'تاریخ' : 'Date'}</label>
        <Input type="date" value={date} onChange={(e:any)=> setDate(e.target.value)} />
      </div>
      <div>
        <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'مرجع' : 'Reference'}</label>
        <Input value={reference} onChange={(e:any)=> setReference(e.target.value)} />
      </div>

      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={() => { onSaved && onSaved() }}>{i18n.language === 'fa' ? 'انصراف' : 'Cancel'}</Button>
        <Button onClick={submit}>{i18n.language === 'fa' ? 'ثبت' : 'Save'}</Button>
      </div>
    </div>
  )
}

export default InvoiceViewPage
