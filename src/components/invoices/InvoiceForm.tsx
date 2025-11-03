import React, { useState, useMemo } from 'react'
import Modal from '@/components/ui/Modal'
import LineItem from './LineItem'
import InvoiceSummary from './InvoiceSummary'
import CustomerLookup from './CustomerLookup'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

const emptyLine = () => ({ description:'', product_id: null, qty: 1, unit_price: 0, tax_rate: 0, line_total: 0 })

const InvoiceForm: React.FC<{ open:boolean, onClose:(created?:any)=>void }> = ({ open, onClose }) => {
  const { i18n } = useTranslation()
  const [customer, setCustomer] = useState<{id?:string, name?:string}>({})
  const [lines, setLines] = useState<any[]>([emptyLine()])
  const [saving, setSaving] = useState(false)

  const recalc = (ls:any[]) => {
    return ls.map(l => {
      const qty = Number(l.qty || 0)
      const unit = Number(l.unit_price || 0)
      const tax = Number(l.tax_rate || 0)
      const base = qty * unit
      const taxAmt = base * (tax/100)
      const total = Math.round((base + taxAmt) * 100) / 100
      return {...l, line_total: total}
    })
  }

  const onLineChange = (idx:number, key:string, val:any) => {
    const cloned = [...lines]
    cloned[idx] = {...cloned[idx], [key]: key === 'description' ? val : (val === '' ? 0 : Number(val))}
    setLines(recalc(cloned))
  }
  const onRemove = (idx:number) => { setLines(ls => ls.filter((_,i)=> i!==idx)) }
  const addLine = () => setLines(ls => [...ls, emptyLine()])

  const subtotal = useMemo(() => lines.reduce((s,l)=> s + Number(l.qty || 0) * Number(l.unit_price || 0), 0), [lines])
  const tax = useMemo(() => lines.reduce((s,l)=> s + (Number(l.qty || 0) * Number(l.unit_price || 0)) * (Number(l.tax_rate || 0)/100), 0), [lines])
  const discount = 0
  const net = subtotal + tax - discount

  const submit = async () => {
    if (!customer.id) { toast.error(i18n.language === 'fa' ? 'مشتری انتخاب نشده' : 'Customer required'); return }
    setSaving(true)
    try {
      const payload = { partner_id: customer.id, invoice_type: 'sale', date: new Date().toISOString().slice(0,10), lines: lines.map(l => ({ product_id: l.product_id, description: l.description, qty: l.qty, unit_price: l.unit_price, tax_rate: l.tax_rate })) }
      const res = await fetch('/api/v1/invoices', { method: 'POST', headers: {'Content-Type':'application/json', 'X-User-Id':'1','X-User-Roles':'finance_post'}, body: JSON.stringify(payload) })
      if (!res.ok) { const err = await res.json().catch(()=>({})); toast.error(err?.detail?.message?.en || 'Error'); return }
      const data = await res.json()
      toast.success(i18n.language === 'fa' ? 'فاکتور ساخته شد' : 'Invoice created')
      onClose && onClose(data)
    } catch (e) { toast.error('Error') } finally { setSaving(false) }
  }

  if (!open) return null
  return (
    <Modal open={open} onOpenChange={(v)=> { if (!v) onClose(); }} title={i18n.language === 'fa' ? 'فاکتور جدید' : 'New Invoice'}>
      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-2">
          <div className="mb-2"><CustomerLookup onSelect={(id,name)=> setCustomer({id,name})} /></div>
          <div className="mb-2">{customer.name && <div className="font-medium">{customer.name}</div>}</div>

          <div className="space-y-2">
            {lines.map((ln, idx) => <LineItem key={idx} idx={idx} item={ln} onChange={onLineChange} onRemove={onRemove} />)}
          </div>

          <div className="flex gap-2 mt-4">
            <Button variant="outline" onClick={addLine}>{i18n.language === 'fa' ? 'افزودن ردیف' : 'Add line'}</Button>
            <Button onClick={submit} disabled={saving}>{i18n.language === 'fa' ? 'ذخیره' : 'Save'}</Button>
          </div>
        </div>

        <div>
          <InvoiceSummary subtotal={subtotal} tax={tax} discount={discount} net={net} />
        </div>
      </div>
    </Modal>
  )
}

export default InvoiceForm
