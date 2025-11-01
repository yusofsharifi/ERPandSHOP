import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import SimpleChart from '@/components/ui/SimpleChart'
import toast from 'react-hot-toast'

type Period = {
  id: string
  company_id: string
  name: string
  start_date: string
  end_date: string
  status: string
}

export default function PayrollPeriodsPage(){
  const { t, i18n } = useTranslation()
  const [periods, setPeriods] = useState<Period[]>([])
  const [loading, setLoading] = useState(false)

  const fmtCurrency = (v:number) => new Intl.NumberFormat(i18n.language === 'fa' ? 'fa-IR' : 'en-US', { style: 'currency', currency: 'IRR', maximumFractionDigits:0 }).format(v)

  const fetchPeriods = async ()=>{
    setLoading(true)
    try{
      const res = await fetch('/api/payroll/periods')
      if(!res.ok) throw new Error('failed')
      const data = await res.json()
      setPeriods(data)
    }catch(e){
      console.error(e)
      toast.error(i18n.language === 'fa' ? 'خطا در دریافت دوره‌ها' : 'Failed to load periods')
    }finally{ setLoading(false) }
  }

  useEffect(()=>{ fetchPeriods() }, [])

  const generate = async (id:string)=>{
    try{
      const res = await fetch(`/api/payroll/periods/${id}/generate`, { method: 'POST' })
      if(!res.ok) throw new Error('failed')
      const d = await res.json()
      toast.success(i18n.language === 'fa' ? 'حقوق تولید شد' : 'Payroll generated')
      fetchPeriods()
    }catch(e){ console.error(e); toast.error(i18n.language === 'fa' ? 'خطا در تولید' : 'Generate failed') }
  }

  const validate = async (payrollId:string)=>{
    try{
      const res = await fetch(`/api/payroll/${payrollId}/validate`, { method: 'POST' })
      if(!res.ok) throw new Error('failed')
      toast.success(i18n.language === 'fa' ? 'تایید شد' : 'Validated')
      fetchPeriods()
    }catch(e){ console.error(e); toast.error(i18n.language === 'fa' ? 'خطا در تایید' : 'Validate failed') }
  }

  // simple chart values: mock gross/net per period
  const chartValues = periods.slice(0,8).map((p, i)=> (i+1)*1000)

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">{t('hr.payroll.periods','Payroll Periods')}</h2>
        <div className="flex gap-2">
          <Button onClick={()=> window.location.href = '/hr/payroll'}>{t('hr.payroll.generate','Generate Payroll')}</Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>{t('hr.payroll.periods_list','Periods')}</CardTitle>
          </CardHeader>
          <CardContent>
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left"><th className="p-2">{t('Name','Name')}</th><th className="p-2">{t('Start','Start')}</th><th className="p-2">{t('End','End')}</th><th className="p-2">{t('Status','Status')}</th><th className="p-2">{t('Actions','Actions')}</th></tr>
              </thead>
              <tbody>
                {periods.map(p=> (
                  <tr key={p.id} className="border-t">
                    <td className="p-2">{p.name}</td>
                    <td className="p-2">{new Date(p.start_date).toLocaleDateString()}</td>
                    <td className="p-2">{new Date(p.end_date).toLocaleDateString()}</td>
                    <td className="p-2">{t(`status.${p.status}`, p.status)}</td>
                    <td className="p-2 flex gap-2">
                      <Button size="sm" onClick={()=> generate(p.id)}>{t('Generate','Generate')}</Button>
                      <Button size="sm" variant="outline" onClick={()=> window.location.href = `/hr/payroll/${p.id}/details`}>{t('Details','Details')}</Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('hr.payroll.trends','Trends')}</CardTitle>
          </CardHeader>
          <CardContent>
            <SimpleChart data={chartValues} />
            <div className="mt-2 text-sm text-muted-foreground">{t('hr.payroll.trend_help','Total gross/net trend')}</div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
