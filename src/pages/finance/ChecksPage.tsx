import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

const ChecksPage: React.FC = () => {
  const { i18n } = useTranslation()
  const [checks, setChecks] = useState<any[]>([])
  const [openNew, setOpenNew] = useState(false)
  const [form, setForm] = useState({ check_no: '', partner_id: '', bank_name: '', issue_date: new Date().toISOString().slice(0,10), due_date: '', amount: '' })

  const fetchList = async () => {
    try {
      const res = await fetch('/api/v1/arap/checks')
      if (!res.ok) return setChecks([])
      const data = await res.json()
      setChecks(data)
    } catch (e) {
      console.error(e)
    }
  }
  useEffect(() => { fetchList() }, [])

  const create = async () => {
    try {
      const payload = { ...form, amount: Number(form.amount) }
      const res = await fetch('/api/v1/arap/checks', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
      if (!res.ok) throw new Error('failed')
      toast.success(i18n.language === 'fa' ? 'چک ثبت شد' : 'Check registered')
      setOpenNew(false)
      setForm({ check_no: '', partner_id: '', bank_name: '', issue_date: new Date().toISOString().slice(0,10), due_date: '', amount: '' })
      fetchList()
    } catch (e) {
      console.error(e)
      toast.error(i18n.language === 'fa' ? 'خطا در ثبت چک' : 'Failed to register check')
    }
  }

  const changeStatus = async (id: string, status: string) => {
    try {
      const res = await fetch(`/api/v1/arap/checks/${id}/status`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ status }) })
      if (!res.ok) throw new Error('failed')
      toast.success(i18n.language === 'fa' ? 'وضعیت تغییر کرد' : 'Status changed')
      fetchList()
    } catch (e) {
      console.error(e)
      toast.error(i18n.language === 'fa' ? 'خطا' : 'Failed')
    }
  }

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{i18n.language === 'fa' ? 'چک‌ها' : 'Checks'}</h2>
        <div>
          <Button onClick={() => setOpenNew(true)}>{i18n.language === 'fa' ? 'چک جدید' : 'New Check'}</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{i18n.language === 'fa' ? 'پیگیری چک‌ها' : 'Check tracking'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left">
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'شماره چک' : 'Check #'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'بانک' : 'Bank'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'تاریخ سررسید' : 'Due Date'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'مبلغ' : 'Amount'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'وضعیت' : 'Status'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'عملیات' : 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {checks.map(c => (
                  <tr key={c.id} className="border-t">
                    <td className="px-2 py-2">{c.check_no}</td>
                    <td className="px-2 py-2">{c.bank_name}</td>
                    <td className="px-2 py-2">{c.due_date}</td>
                    <td className="px-2 py-2">{c.amount}</td>
                    <td className="px-2 py-2">{c.status}</td>
                    <td className="px-2 py-2">
                      <div className="flex gap-2">
                        {c.status !== 'deposited' && <Button size="sm" onClick={() => changeStatus(c.id, 'deposited')}>{i18n.language === 'fa' ? 'واریز' : 'Deposit'}</Button>}
                        {c.status !== 'returned' && <Button size="sm" variant="destructive" onClick={() => changeStatus(c.id, 'returned')}>{i18n.language === 'fa' ? 'برگشت' : 'Returned'}</Button>}
                      </div>
                    </td>
                  </tr>
                ))}
                {checks.length === 0 && <tr><td colSpan={6} className="p-4 text-center text-sm text-muted">{i18n.language === 'fa' ? 'موردی یافت نشد' : 'No checks found'}</td></tr>}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <Modal open={openNew} onOpenChange={setOpenNew} title={i18n.language === 'fa' ? 'چک جدید' : 'New Check'}>
        <div className="space-y-3">
          <div>
            <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'شماره چک' : 'Check #'}</label>
            <Input value={form.check_no} onChange={(e:any)=> setForm({...form, check_no: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'طرف حساب (شناسه)' : 'Partner (id)'}</label>
            <Input value={form.partner_id} onChange={(e:any)=> setForm({...form, partner_id: e.target.value})} />
          </div>
          <div>
            <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'بانک' : 'Bank'}</label>
            <Input value={form.bank_name} onChange={(e:any)=> setForm({...form, bank_name: e.target.value})} />
          </div>
          <div className="flex gap-2">
            <div>
              <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'تاریخ صدور' : 'Issue Date'}</label>
              <Input type="date" value={form.issue_date} onChange={(e:any)=> setForm({...form, issue_date: e.target.value})} />
            </div>
            <div>
              <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'تاریخ سررسید' : 'Due Date'}</label>
              <Input type="date" value={form.due_date} onChange={(e:any)=> setForm({...form, due_date: e.target.value})} />
            </div>
          </div>
          <div>
            <label className="block text-sm mb-1">{i18n.language === 'fa' ? 'مبلغ' : 'Amount'}</label>
            <Input type="number" value={form.amount} onChange={(e:any)=> setForm({...form, amount: e.target.value})} />
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setOpenNew(false)}>{i18n.language === 'fa' ? 'لغو' : 'Cancel'}</Button>
            <Button onClick={create}>{i18n.language === 'fa' ? 'ثبت' : 'Save'}</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default ChecksPage
