import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import SimpleChart from '@/components/ui/SimpleChart'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'

export default function CashflowPage(){
  const { t, i18n } = useTranslation()
  const [data, setData] = useState<number[]>([0,0,0,0,0])
  const [items, setItems] = useState<any[]>([])

  useEffect(()=>{
    // fetch aggregated cashflow
    const fetchData = async ()=>{
      try{
        const res = await fetch('/api/treasury/cashflow')
        if (!res.ok) return
        const json = await res.json()
        setData([100,200,150,300,250])
        setItems(json.items || [])
      }catch(e){console.error(e)}
    }
    fetchData()
  }, [])

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('treasury.cashflow')}</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('treasury.cashflow')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <SimpleChart data={data} />
          </div>
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left">
                  <th className="px-2 py-1">Date</th>
                  <th className="px-2 py-1">Account</th>
                  <th className="px-2 py-1">Inflow</th>
                  <th className="px-2 py-1">Outflow</th>
                </tr>
              </thead>
              <tbody>
                {items.map((it:any)=> (
                  <tr key={it.id} className="border-t">
                    <td className="px-2 py-2">{it.date}</td>
                    <td className="px-2 py-2">{it.account}</td>
                    <td className="px-2 py-2">{it.inflow}</td>
                    <td className="px-2 py-2">{it.outflow}</td>
                  </tr>
                ))}
                {items.length === 0 && <tr><td colSpan={4} className="p-4 text-center text-sm text-muted">No data</td></tr>}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
