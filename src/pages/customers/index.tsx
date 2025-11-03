import React, { useEffect, useState, useMemo } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import CustomerForm from '@/components/customers/CustomerForm'
import CustomerTable from '@/components/customers/CustomerTable'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

const CustomersPage: React.FC = () => {
  const { t, i18n } = useTranslation()
  const [customers, setCustomers] = useState<any[]>([])
  const [q, setQ] = useState('')
  const [status, setStatus] = useState<string | ''>('')
  const [page, setPage] = useState(1)
  const [perPage] = useState(15)
  const [openNew, setOpenNew] = useState(false)
  const [loading, setLoading] = useState(false)

  const fetchList = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (q) params.set('search', q)
      if (status) params.set('status', status)
      params.set('limit', String(perPage))
      params.set('offset', String((page - 1) * perPage))
      const res = await fetch('/api/v1/customers?' + params.toString())
      if (!res.ok) { setCustomers([]); toast.error(t('error') || 'Error'); return }
      const data = await res.json()
      setCustomers(Array.isArray(data) ? data : (data.items || data))
    } catch (e) {
      setCustomers([])
      toast.error(t('error') || 'Error')
    } finally { setLoading(false) }
  }

  useEffect(() => { const id = setTimeout(fetchList, 300); return () => clearTimeout(id) }, [q, status, page])

  const onCreated = (c: any) => { fetchList(); toast.success(i18n.language === 'fa' ? 'مشتری ذخیره شد' : 'Customer saved') }

  const totalPages = useMemo(() => Math.max(1, Math.ceil(customers.length / perPage)), [customers, perPage])

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{i18n.language === 'fa' ? 'مشتریان' : 'Customers'}</h2>
        <div className="flex items-center gap-2">
          <Button onClick={() => setOpenNew(true)}>{i18n.language === 'fa' ? 'مشتری جدید' : 'New Customer'}</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{i18n.language === 'fa' ? 'لیست مشتریان' : 'Customer list'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input placeholder={i18n.language === 'fa' ? 'جستجو...' : 'Search...'} value={q} onChange={(e:any)=> setQ(e.target.value)} />
            <select value={status} onChange={(e)=> setStatus(e.target.value)} className="p-2 border rounded">
              <option value="">{i18n.language === 'fa' ? 'همه وضعیت‌ها' : 'All statuses'}</option>
              <option value="active">{i18n.language === 'fa' ? 'فعال' : 'Active'}</option>
              <option value="deleted">{i18n.language === 'fa' ? 'حذف شده' : 'Deleted'}</option>
            </select>
            <Button variant="outline" onClick={fetchList}>{i18n.language === 'fa' ? 'بارگذاری' : 'Refresh'}</Button>
          </div>

          <CustomerTable items={customers} loading={loading} />
        </CardContent>
        <CardFooter>
          <div className="flex items-center justify-between w-full">
            <div>{i18n.language === 'fa' ? `صفحه ${page}/${totalPages}` : `Page ${page}/${totalPages}`}</div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setPage(p => Math.max(1, p-1))}>{i18n.language === 'fa' ? 'قبلی' : 'Prev'}</Button>
              <Button variant="outline" onClick={() => setPage(p => p+1)}>{i18n.language === 'fa' ? 'بعدی' : 'Next'}</Button>
            </div>
          </div>
        </CardFooter>
      </Card>

      <CustomerForm open={openNew} setOpen={setOpenNew} onCreated={onCreated} />
    </div>
  )
}

export default CustomersPage
