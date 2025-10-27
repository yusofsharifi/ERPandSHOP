import React, { useEffect, useState, useMemo } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import PartnerFormModal from '@/components/finance/PartnerFormModal'
import PartnerQuickView from '@/components/finance/PartnerQuickView'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

type Partner = { id: string; name: string; partner_type: string; email?: string; credit_limit?: number; balance_amount?: number; active?: boolean }

const PartnersPage: React.FC = () => {
  const { t, i18n } = useTranslation()
  const [partners, setPartners] = useState<Partner[]>([])
  const [q, setQ] = useState('')
  const [type, setType] = useState<string | ''>('')
  const [active, setActive] = useState<string | ''>('')
  const [page, setPage] = useState(1)
  const [perPage] = useState(15)
  const [openNew, setOpenNew] = useState(false)
  const [quickId, setQuickId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const fetchList = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (q) params.set('search', q)
      if (type) params.set('type', type)
      if (active) params.set('active', active)
      params.set('page', String(page))
      params.set('per_page', String(perPage))
      const res = await fetch('/api/v1/arap/partners?' + params.toString())
      if (!res.ok) { setPartners([]); return }
      const data = await res.json()
      // support both {items:[], total} and array
      setPartners(Array.isArray(data) ? data : (data.items || data))
    } catch (e) {
      setPartners([])
      toast.error(t('error') || 'Error')
    } finally { setLoading(false) }
  }

  useEffect(() => { const id = setTimeout(fetchList, 300); return () => clearTimeout(id) }, [q, type, active, page])

  const onCreated = (p: any) => { fetchList(); toast.success(i18n.language === 'fa' ? 'طرف حساب ذخیره شد' : 'Partner saved') }

  const totalPages = useMemo(() => Math.ceil(partners.length / perPage) || 1, [partners, perPage])

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{i18n.language === 'fa' ? 'طرف حساب‌ها' : 'Partners'}</h2>
        <div className="flex items-center gap-2">
          <Button onClick={() => setOpenNew(true)}>{i18n.language === 'fa' ? 'طرف حساب جدید' : 'New Partner'}</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{i18n.language === 'fa' ? 'لیست طرف حساب‌ها' : 'Partner list'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input placeholder={i18n.language === 'fa' ? 'جستجو...' : 'Search...'} value={q} onChange={(e:any)=> setQ(e.target.value)} />
            <select value={type} onChange={(e)=> setType(e.target.value)} className="p-2 border rounded">
              <option value="">{i18n.language === 'fa' ? 'همه نوع‌ها' : 'All types'}</option>
              <option value="customer">{i18n.language === 'fa' ? 'مشتری' : 'Customer'}</option>
              <option value="supplier">{i18n.language === 'fa' ? 'تأمین‌کننده' : 'Supplier'}</option>
            </select>
            <select value={active} onChange={(e)=> setActive(e.target.value)} className="p-2 border rounded">
              <option value="">{i18n.language === 'fa' ? 'همه' : 'All'}</option>
              <option value="1">{i18n.language === 'fa' ? 'فعال' : 'Active'}</option>
              <option value="0">{i18n.language === 'fa' ? 'غیرفعال' : 'Inactive'}</option>
            </select>
            <Button variant="outline" onClick={fetchList}>{i18n.language === 'fa' ? 'بارگذاری' : 'Refresh'}</Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full table-auto" role="table" aria-label="Partners table">
              <thead>
                <tr className="text-left">
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'نام' : 'Name'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'نوع' : 'Type'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'حد اعتباری' : 'Credit Limit'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'مانده' : 'Balance'}</th>
                  <th className="px-2 py-1">{i18n.language === 'fa' ? 'عملیات' : 'Actions'}</th>
                </tr>
              </thead>
              <tbody>
                {loading && <tr><td colSpan={5} className="p-4">{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</td></tr>}
                {!loading && partners.length === 0 && <tr><td colSpan={5} className="p-4">{i18n.language === 'fa' ? 'موردی یافت نشد' : 'No results'}</td></tr>}
                {!loading && partners.map(p => (
                  <tr key={p.id} className="border-t">
                    <td className="px-2 py-2">{p.name}</td>
                    <td className="px-2 py-2">{p.partner_type}</td>
                    <td className="px-2 py-2">{p.credit_limit ?? '-'}</td>
                    <td className="px-2 py-2">{p.balance_amount ?? '-'}</td>
                    <td className="px-2 py-2">
                      <div className="flex gap-2">
                        <Button size="sm" onClick={() => setQuickId(p.id)}>{i18n.language === 'fa' ? 'پیش‌نمایش' : 'Quick'}</Button>
                        <a className="underline text-primary" href={`/finance/partners/${p.id}/aging`}>{i18n.language === 'fa' ? ' aging' : 'Aging'}</a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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

      <PartnerFormModal open={openNew} setOpen={setOpenNew} onCreated={onCreated} />
      {quickId && <div className="fixed right-6 bottom-6"><PartnerQuickView partnerId={quickId} onClose={()=> setQuickId(null)} /></div>}
    </div>
  )
}

export default PartnersPage
