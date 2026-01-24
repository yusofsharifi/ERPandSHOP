import React, { useState } from 'react'
import Modal from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

const PaymentModal: React.FC<{ open:boolean, invoiceId:string, partnerId:string, onClose:(saved?:any)=>void }> = ({ open, invoiceId, partnerId, onClose }) => {
  const { i18n } = useTranslation()
  const [amount, setAmount] = useState('')
  const [method, setMethod] = useState('cash')
  const [saving, setSaving] = useState(false)

  const submit = async () => {
    if (!amount) { toast.error(i18n.language==='fa' ? 'مقدار وارد نشده' : 'Amount required'); return }
    setSaving(true)
    try {
      const payload = { partner_id: partnerId, amount: Number(amount), method, payment_date: new Date().toISOString().slice(0,10) }
      const res = await fetch(`/api/v1/invoices/${invoiceId}/pay`, { method: 'POST', headers: {'Content-Type':'application/json','X-User-Id':'1','X-User-Roles':'finance_post'}, body: JSON.stringify(payload) })
      if (!res.ok) { const err = await res.json().catch(()=>({})); toast.error(err?.detail?.message?.en || 'Error'); return }
      const data = await res.json()
      toast.success(i18n.language==='fa' ? 'پرداخت ثبت شد' : 'Payment recorded')
      onClose && onClose(data)
    } catch (e) { toast.error('Error') } finally { setSaving(false) }
  }

  if (!open) return null
  return (
    <Modal open={open} onOpenChange={(v)=> { if (!v) onClose(); }} title={i18n.language==='fa' ? 'ثبت پرداخت' : 'Record payment'}>
      <div className="grid gap-2">
        <Input placeholder={i18n.language==='fa' ? 'مبلغ' : 'Amount'} value={amount} onChange={(e:any)=> setAmount(e.target.value)} />
        <select value={method} onChange={(e)=> setMethod(e.target.value)} className="p-2 border rounded">
          <option value="cash">{i18n.language==='fa' ? 'نقد' : 'Cash'}</option>
          <option value="bank">{i18n.language==='fa' ? 'بانک' : 'Bank'}</option>
          <option value="check">{i18n.language==='fa' ? 'چک' : 'Check'}</option>
          <option value="online">{i18n.language==='fa' ? 'آنلا��ن' : 'Online'}</option>
        </select>
        <div className="flex gap-2 justify-end mt-2">
          <Button variant="outline" onClick={()=> onClose()}>{i18n.language==='fa' ? 'انصراف' : 'Cancel'}</Button>
          <Button onClick={submit} disabled={saving}>{i18n.language==='fa' ? 'ثبت' : 'Save'}</Button>
        </div>
      </div>
    </Modal>
  )
}

export default PaymentModal
