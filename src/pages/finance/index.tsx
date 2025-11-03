import React from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

export default function FinancePage(){
  const { t } = useTranslation()
  return (
    <div>
      <h1 className="text-xl font-bold">{t('nav.finance', 'Finance')}</h1>
      <p className="text-sm text-muted-foreground">Quick links</p>
      <div className="mt-4 space-x-2">
        <Link to="/finance/accounts" className="px-3 py-2 bg-primary text-primary-foreground rounded">Accounts</Link>
        <Link to="/finance/journal-entries" className="px-3 py-2 border rounded">Journal Entries</Link>
      </div>
    </div>
  )
}
