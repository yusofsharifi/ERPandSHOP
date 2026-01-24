import React from 'react'
import { useTranslation } from 'react-i18next'

export default function InventoryPage(){
  const { t } = useTranslation()
  return (
    <div>
      <h1 className="text-xl font-bold">{t('nav.inventory', 'Inventory')}</h1>
      <p className="text-sm text-muted-foreground">Inventory management placeholder page.</p>
    </div>
  )
}
