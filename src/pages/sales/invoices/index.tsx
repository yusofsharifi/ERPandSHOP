import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import InvoiceStatusBadge from '@/components/invoices/InvoiceStatusBadge'
import InvoiceForm from '@/components/invoices/InvoiceForm'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { Link } from 'react-router-dom'

const InvoiceListPage: React.FC = () => {
  const { i18n } = useTranslation()
  const [q, setQ] = useState('')
  const [status, setStatus] = useState('')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [items, setItems] = useState<any[]>([])
  const [openNew, setOpenNew] = useState(false)

  const fetchList = async () => {
    try {
      const params = new URLSearchParams()
      if (status) params.set('status', status)
      if (dateFrom) params.set('date_from', dateFrom)
      if (dateTo) params.set('date_to', dateTo)
      if (q) params.set('customer_id', q)
      const res = await fetch('/api/v1/invoices?' + params.toString())
      if (!res.ok) { setItems([]); return }
      const data = await res.json()
      setItems(Array.isArray(data) ? data : (data.items || data))
    } catch (e) { setItems([]); toast.error(i18n.language === 'fa' ? 'خطا در بارگذاری' : 'Failed to load') }
  }

  useEffect(()=>{ fetchList() }, [])

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{i18n.language === 'fa' ? 'فاکتورها' : 'Invoices'}</h2>
        <div><Button onClick={()=> setOpenNew(true)}>{i18n.language === 'fa' ? 'فاکتور جدید' : 'New Invoice'}</Button></div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{i18n.language === 'fa' ? 'لیست فاکتورها' : 'Invoice list'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input placeholder={i18n.language === 'fa' ? 'جستجوی مشتری (id)' : 'Customer id'} value={q} onChange={(e:any)=> setQ(e.target.value)} />
            <select value={status} onChange={(e)=> setStatus(e.target.value)} className="p-2 border rounded">
              <option value="">{i18n.language === 'fa' ? 'همه وضعیت‌ها' : 'All statuses'}</option>
              <option value="draft">{i18n.language === 'fa' ? 'پیش‌نویس' : 'Draft'}</option>
              <option value="open">{i18n.language === 'fa' ? 'ثبت شده' : 'Posted'}</option>
              <option value="partial">{i18n.language === 'fa' ? 'نیمه‌پرداخت' : 'Partial'}</option>
              <option value="paid">{i18n.language === 'fa' ? 'پرداخت‌شده' : 'Paid'}</option>
            </select>
            <Input type="date" value={dateFrom} onChange={(e:any)=> setDateFrom(e.target.value)} />
            <Input type="date" value={dateTo} onChange={(e:any)=> setDateTo(e.target.value)} />
            <Button variant="outline" onClick={fetchList}>{i18n.language === 'fa' ? 'فیلتر' : 'Filter'}</Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left">
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'شماره' : 'Invoice No'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'مشتری' : 'Customer'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'تاریخ' : 'Date'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'جمع' : 'Total'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'وضعیت' : 'Status'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'عملیات' : 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {items.map(inv => (
                  <tr key={inv.id} className="border-t">
                    <td className="px-2 py-2">{inv.invoice_no || inv.id}</td>
                    <td className="px-2 py-2">{inv.partner_id}</td>
                    <td className="px-2 py-2">{inv.date}</td>
                    <td className="px-2 py-2">{inv.total_amount}</td>
                    <td className="px-2 py-2"><InvoiceStatusBadge status={inv.status} /></td>
                    <td className="px-2 py-2"><div className="flex gap-2"><Link to={`/sales/invoices/${inv.id}`} className="underline">{i18n.language === 'fa' ? 'نمایش' : 'View'}</Link></div></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
        <CardFooter>
          <div />
        </CardFooter>
      </Card>

      <InvoiceForm open={openNew} onClose={()=> { setOpenNew(false); fetchList() }} />
    </div>
  )
}

export default InvoiceListPage
