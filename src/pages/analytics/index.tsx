import React from 'react'
import { useTranslation } from 'react-i18next'

export default function AnalyticsPage(){
  const { t } = useTranslation()
  return (
    <div>
      <h1 className="text-xl font-bold">{t('nav.analytics', 'Analytics')}</h1>
      <p className="text-sm text-muted-foreground">Analytics dashboard placeholder.</p>
    </div>
  )
}
