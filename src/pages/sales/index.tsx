import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function SalesPage(){
  const { t } = useTranslation()
  return (
    <div>
      <h1 className="text-xl font-bold">{t('nav.sales', 'Sales')}</h1>
      <p className="text-sm text-muted-foreground">Sales overview. Quick links:</p>
      <div className="mt-4 space-x-2">
        <Link to="/sales/orders" className="px-3 py-2 border rounded">Orders</Link>
        <Link to="/sales/invoices" className="px-3 py-2 border rounded">Invoices</Link>
      </div>
    </div>
  )
}
