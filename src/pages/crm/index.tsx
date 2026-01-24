import React from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

export default function CrmPage(){
  const { t } = useTranslation()
  return (
    <div>
      <h1 className="text-xl font-bold">{t('nav.crm', 'CRM')}</h1>
      <p className="text-sm text-muted-foreground">Customer relationship management placeholder.</p>
      <div className="mt-4"><Link to="/customers" className="px-3 py-2 border rounded">Open Customers</Link></div>
    </div>
  )
}
