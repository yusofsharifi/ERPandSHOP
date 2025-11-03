import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { useTranslation } from 'react-i18next'
import CustomerNotes from '@/components/customers/CustomerNotes'
import TransactionList from '@/components/customers/TransactionList'
import toast from 'react-hot-toast'

const CustomerDetail: React.FC = () => {
  const { id } = useParams()
  const { t, i18n } = useTranslation()
  const [customer, setCustomer] = useState<any | null>(null)

  const fetchCustomer = async () => {
    if (!id) return
    try {
      const res = await fetch(`/api/v1/customers/${id}`)
      if (!res.ok) { toast.error(t('error') || 'Error'); return }
      const data = await res.json()
      setCustomer(data)
    } catch (e) {
      toast.error(t('error') || 'Error')
    }
  }

  useEffect(() => { fetchCustomer() }, [id])

  if (!id) return <div />

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{i18n.language === 'fa' ? 'جزئیات مشتری' : 'Customer Detail'}</h2>
        <div>
          <Link to="/customers">{i18n.language === 'fa' ? 'بازگشت به لیست' : 'Back to list'}</Link>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{customer ? (customer.name || customer.partner?.name) : (i18n.language === 'fa' ? 'مشخصات' : 'Profile')}</CardTitle>
        </CardHeader>
        <CardContent>
          {customer ? (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div><strong>{i18n.language === 'fa' ? 'نام' : 'Name'}:</strong> {customer.name}</div>
                <div><strong>{i18n.language === 'fa' ? 'تلفن' : 'Mobile'}:</strong> {customer.mobile}</div>
                <div><strong>{i18n.language === 'fa' ? 'ایمیل' : 'Email'}:</strong> {customer.email}</div>
                <div><strong>{i18n.language === 'fa' ? 'آدرس' : 'Address'}:</strong> {customer.address}</div>
              </div>
              <div>
                <div><strong>{i18n.language === 'fa' ? 'شناسه ملی' : 'National ID'}:</strong> {customer.national_id}</div>
                <div><strong>{i18n.language === 'fa' ? 'شماره ثبت' : 'Registration No'}:</strong> {customer.registration_no}</div>
                <div><strong>{i18n.language === 'fa' ? 'حد اعتباری' : 'Credit Limit'}:</strong> {customer.credit_limit}</div>
                <div><strong>{i18n.language === 'fa' ? 'شماره مشتری' : 'Customer No'}:</strong> {customer.customer_no}</div>
              </div>
            </div>
          ) : (<div>{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>)}
        </CardContent>
      </Card>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <CustomerNotes customerId={id} />
        <TransactionList customerId={id} />
      </div>
    </div>
  )
}

export default CustomerDetail
