import React from 'react'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'

const CustomerTable: React.FC<{ items:any[]; loading?:boolean }> = ({ items, loading=false }) => {
  const { i18n } = useTranslation()
  if (loading) return <div className="p-4">{i18n.language==='fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>
  if (!items || items.length === 0) return <div className="p-4">{i18n.language==='fa' ? 'موردی یافت نشد' : 'No results'}</div>
  return (
    <div className="overflow-x-auto">
      <table className="w-full table-auto" role="table" aria-label="Customers table">
        <thead>
          <tr className="text-left">
            <th className="px-2 py-1">{i18n.language==='fa' ? 'نام' : 'Name'}</th>
            <th className="px-2 py-1">{i18n.language==='fa' ? 'تلفن' : 'Mobile'}</th>
            <th className="px-2 py-1">{i18n.language==='fa' ? 'ایمیل' : 'Email'}</th>
            <th className="px-2 py-1">{i18n.language==='fa' ? 'حد اعتباری' : 'Credit Limit'}</th>
            <th className="px-2 py-1">{i18n.language==='fa' ? 'عملیات' : 'Actions'}</th>
          </tr>
        </thead>
        <tbody>
          {items.map(it => (
            <tr key={it.id} className="border-t">
              <td className="px-2 py-2">{it.name}</td>
              <td className="px-2 py-2">{it.mobile ?? '-'}</td>
              <td className="px-2 py-2">{it.email ?? '-'}</td>
              <td className="px-2 py-2">{it.credit_limit ?? '-'}</td>
              <td className="px-2 py-2">
                <div className="flex gap-2">
                  <a className="underline text-primary" href={`/customers/${it.id}`}>{i18n.language==='fa' ? 'نمایش' : 'View'}</a>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default CustomerTable
