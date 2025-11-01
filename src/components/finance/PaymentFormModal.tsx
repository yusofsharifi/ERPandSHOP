import React, { useEffect, useState } from 'react'
import Modal from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

export default function PaymentFormModal({ open, setOpen, invoiceId, onSaved }: { open: boolean; setOpen: (v:boolean)=>void; invoiceId?: string | null; onSaved?: ()=>void }){
  const { i18n } = useTranslation()
  const [amount, setAmount] = useState('')
  const [method, setMethod] = useState('cash')
  const [date, setDate] = useState(new Date().toISOString().slice(0,10))
  const [reference, setReference] = useState('')
  const [invoice, setInvoice] = useState<any>(null)

  useEffect(() => {
    const fetchInv = async () => {
      if (!invoiceId) return setInvoice(null)
      try {
        const res = await fetch('/api/v1/arap/invoices')
        if (!res.ok) return
        const list = await res.json()
        const found = list.find((i:any)=> i.id === invoiceId)
        setInvoice(found)
      } catch (e) { console.error(e) }
    }
    fetchInv()
  }, [invoiceId])

  const submit = async () => {
    const a = Number(amount || 0)
    if (a <= 0) return toast.error(i18n.language === 'fa' ? 'مبلغ باید بزرگتر از صفر باشد' : 'Amount must be > 0')
    if (invoice) {
      const rem = Number(invoice.balance_amount || invoice.total_amount || 0)
      if (a > rem) return toast.error(i18n.language === 'fa' ? 'پرداخت بیشتر از مانده است' : 'Payment exceeds remaining balance')
    }
    try {
      const payload: any = { amount: a, method, payment_date: date, reference }
      if (invoice) payload.invoice_id = invoice.id
      if (invoice) payload.partner_id = invoice.partner_id
      const res = await fetch('/api/v1/arap/payments', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (!res.ok) throw new Error('failed')
      toast.success(i18n.language === 'fa' ? 'پرداخت ثبت شد' : 'Payment recorded')
      onSaved && onSaved()
      setOpen(false)
    } catch (e) {
      console.error(e)
      toast.error(i18n.language === 'fa' ? 'خطا در ثبت پرداخت' : 'Failed to record payment')
    }
  }

  return (
    <Modal open={open} onOpenChange={setOpen} title={i18n.language === 'fa' ? 'ثبت پرداخت' : 'Register Payment'}>
      <div className="space-y-3">
        {invoice && <div className="p-2 border rounded text-sm">{i18n.language === 'fa' ? 'فاکتور' : 'Invoice'}: {invoice.invoice_no} — {i18n.language === 'fa' ? 'مانده' : 'Balance'}: {invoice.balance_amount}</div>}
        <div>
          <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'مبلغ' : 'Amount'}</label>
          <Input type="number" value={amount} onChange={(e:any)=> setAmount(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'روش' : 'Method'}</label>
          <select value={method} onChange={(e)=> setMethod(e.target.value)} className="p-2 border rounded w-full">
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
          <Button variant="outline" onClick={() => setOpen(false)}>{i18n.language === 'fa' ? 'انصراف' : 'Cancel'}</Button>
          <Button onClick={submit}>{i18n.language === 'fa' ? 'ثبت' : 'Save'}</Button>
        </div>
      </div>
    </Modal>
  )
}
