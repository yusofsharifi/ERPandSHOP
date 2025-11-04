import React, { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

interface Line { id: string; description: string; qty: number; unit_price: number; tax_rate: number; line_total: number }

const InvoiceNewPage: React.FC = () => {
  const { i18n, t } = useTranslation()
  const [step, setStep] = useState(0)
  const [partnerId, setPartnerId] = useState('')
  const [type, setType] = useState('sale')
  const [lines, setLines] = useState<Line[]>([])
  const [openPayment, setOpenPayment] = useState(false)
  const navigate = useNavigate()

  const addLine = () => {
    setLines([...lines, { id: Date.now().toString(), description: '', qty: 1, unit_price: 0, tax_rate: 0, line_total: 0 }])
  }
  const removeLine = (id: string) => setLines(lines.filter(l => l.id !== id))

  const updateLine = (id: string, patch: Partial<Line>) => {
    setLines(lines.map(l => {
      if (l.id !== id) return l
      const qty = patch.qty !== undefined ? patch.qty : l.qty
      const unit_price = patch.unit_price !== undefined ? patch.unit_price : l.unit_price
      const tax_rate = patch.tax_rate !== undefined ? patch.tax_rate : l.tax_rate
      const line_total = Number((qty * unit_price * (1 + (tax_rate / 100))).toFixed(2))
      return { ...l, ...patch, qty, unit_price, tax_rate, line_total }
    }))
  }
  const totals = lines.reduce((acc, l) => acc + (l.line_total || 0), 0)

  const create = async () => {
    if (!partnerId) return toast.error(i18n.language === 'fa' ? 'لطفاً طرف حساب را وارد کنید' : 'Please provide partner id')
    if (lines.length === 0) return toast.error(i18n.language === 'fa' ? 'حداقل یک سطر اضافه کنید' : 'Add at least one line')

    const payload = { partner_id: partnerId, invoice_type: type, date: new Date().toISOString().slice(0,10), lines: lines.map(l => ({ product_id: null, description: l.description, qty: l.qty, unit_price: l.unit_price, tax_rate: l.tax_rate })) }
    try {
      const res = await fetch('/api/v1/arap/invoices', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) })
      if (!res.ok) throw new Error('failed')
      const inv = await res.json()
      toast.success(i18n.language === 'fa' ? 'فاکتور ایجاد شد' : 'Invoice created')
      navigate(`/finance/invoices/${inv.id}`)
    } catch (e) {
      console.error(e)
      toast.error(i18n.language === 'fa' ? 'خطا در ایجاد فاکتور' : 'Failed to create invoice')
    }
  }

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('new_invoice') || (i18n.language === 'fa' ? 'فاکتور جدید' : 'New Invoice')}</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{t('invoice_wizard') || (i18n.language === 'fa' ? 'جادوگر فاکتور' : 'Invoice Wizard')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">{i18n.language === 'fa' ? `مرحله ${step+1} / 3` : `Step ${step+1} / 3`}</div>
          {step === 0 && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'طرف حساب (شناسه)' : 'Partner (id)'}</label>
                <Input value={partnerId} onChange={(e)=> setPartnerId(e.target.value)} placeholder={i18n.language === 'fa' ? 'شناسه طرف حساب' : 'partner id'} />
              </div>
              <div>
                <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'نوع' : 'Type'}</label>
                <select value={type} onChange={(e)=> setType(e.target.value)} className="p-2 border rounded">
                  <option value="sale">{i18n.language === 'fa' ? 'فروش' : 'Sale'}</option>
                  <option value="purchase">{i18n.language === 'fa' ? 'خرید' : 'Purchase'}</option>
                </select>
              </div>
            </div>
          )}
          {step === 1 && (
            <div>
              <div className="mb-2 flex justify-between">
                <h4 className="font-semibold">{i18n.language === 'fa' ? 'سطرها' : 'Lines'}</h4>
                <Button onClick={addLine}>{t('add') || (i18n.language === 'fa' ? 'افزودن سطر' : 'Add Line')}</Button>
              </div>
              <div className="space-y-2">
                {lines.map(l => (
                  <div key={l.id} className="p-2 border rounded flex gap-2 items-center">
                    <Input placeholder={i18n.language === 'fa' ? 'شرح' : 'Description'} value={l.description} onChange={(e)=> updateLine(l.id, { description: e.target.value })} />
                    <Input type="number" value={l.qty} onChange={(e)=> updateLine(l.id, { qty: Number(e.target.value) })} className="w-24" />
                    <Input type="number" value={l.unit_price} onChange={(e)=> updateLine(l.id, { unit_price: Number(e.target.value) })} className="w-28" />
                    <Input type="number" value={l.tax_rate} onChange={(e)=> updateLine(l.id, { tax_rate: Number(e.target.value) })} className="w-24" />
                    <div className="w-32 text-sm">{i18n.language === 'fa' ? 'مجموع' : 'Line total'}: {l.line_total.toFixed(2)}</div>
                    <Button variant="outline" onClick={() => removeLine(l.id)}>{i18n.language === 'fa' ? 'حذف' : 'Remove'}</Button>
                  </div>
                ))}
              </div>
            </div>
          )}
          {step === 2 && (
            <div>
              <h4 className="font-semibold mb-2">{i18n.language === 'fa' ? 'جمع‌ها' : 'Totals'}</h4>
              <div className="mb-2">{i18n.language === 'fa' ? 'جمع جزئی' : 'Subtotal'}: {totals.toFixed(2)}</div>
              <div className="mb-2">{i18n.language === 'fa' ? 'جمع' : 'Total'}: {totals.toFixed(2)}</div>
            </div>
          )}

          <div className="flex justify-end gap-2 mt-4">
            {step > 0 && <Button variant="outline" onClick={() => setStep(s => s-1)}>{t('back') || (i18n.language === 'fa' ? 'بازگشت' : 'Back')}</Button>}
            {step < 2 ? <Button onClick={() => setStep(s => s+1)}>{t('next') || (i18n.language === 'fa' ? 'بعدی' : 'Next')}</Button> : <Button onClick={create}>{t('create') || (i18n.language === 'fa' ? 'ایجاد' : 'Create')}</Button>}
          </div>
        </CardContent>
      </Card>

      <Modal open={openPayment} onOpenChange={setOpenPayment} title={i18n.language === 'fa' ? 'ثبت پرداخت' : 'Register Payment'}>
        <div>{i18n.language === 'fa' ? 'فرم پرداخت' : 'Payment form'}</div>
      </Modal>
    </div>
  )
}

export default InvoiceNewPage
