import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'

const STORAGE_KEY = 'hr_tax_settings'

export default function TaxSettingsPage(){
  const { t } = useTranslation()
  const [taxRate, setTaxRate] = useState(10)

  useEffect(()=>{
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) setTaxRate(Number(raw))
  }, [])

  useEffect(()=>{ localStorage.setItem(STORAGE_KEY, String(taxRate)) }, [taxRate])

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">{t('Tax Settings','Tax Settings')}</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Tax Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-2 items-center">
            <label>Tax Rate (%)</label>
            <input className="input" type="number" value={taxRate} onChange={(e)=> setTaxRate(Number(e.target.value))} />
            <div><Button onClick={()=> alert('Saved')}>Save</Button></div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
