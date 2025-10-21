import React from 'react'
import { useTranslation } from 'react-i18next'

export default function TotalsBar({ totalDebit, totalCredit }: { totalDebit: number; totalCredit: number }){
  const { t } = useTranslation()
  const diff = Number((totalDebit - totalCredit).toFixed(2))
  return (
    <div className="sticky bottom-0 bg-background border-t p-3 flex justify-between items-center">
      <div className="space-x-4 text-sm">
        <span className="font-medium">{t('gl.labels.total_debit') || 'Total Debit'}: {totalDebit.toFixed(2)}</span>
        <span className="font-medium">{t('gl.labels.total_credit') || 'Total Credit'}: {totalCredit.toFixed(2)}</span>
      </div>
      <div className={diff === 0 ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
        {t('gl.labels.difference') || 'Difference'}: {diff.toFixed(2)}
      </div>
    </div>
  )
}
