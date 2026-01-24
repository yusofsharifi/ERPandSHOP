import React from 'react'
import { useTranslation } from 'react-i18next'

export default function EcommercePage(){
  const { t } = useTranslation()
  return (
    <div>
      <h1 className="text-xl font-bold">{t('nav.ecommerce', 'E-Commerce')}</h1>
      <p className="text-sm text-muted-foreground">E-Commerce section placeholder.</p>
    </div>
  )
}
