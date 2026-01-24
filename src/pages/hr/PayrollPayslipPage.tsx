import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'

export default function PayrollPayslipPage(){
  const { id } = useParams()
  const { t, i18n } = useTranslation()
  const [payslip, setPayslip] = useState<any | null>(null)

  useEffect(()=>{
    const fetchPayslip = async ()=>{
      try{
        const res = await fetch(`/api/payroll/${id}`)
        if(!res.ok) throw new Error('failed')
        const data = await res.json()
        // map to payslip friendly
        const p = data.payroll ? { id: data.payroll.id, name: 'Employee', email:'', position:'', period: '', gross: Number(data.payroll.gross_salary || 0), tax:0, net: Number(data.payroll.net_salary || 0), details: data.lines || [] } : null
        setPayslip(p)
      }catch(e){ console.error(e); toast.error(i18n.language === 'fa' ? 'خطا در دریافت' : 'Failed to load') }
    }
    if(id) fetchPayslip()
  }, [id])

  if(!payslip) return <div className="p-4">{t('Loading','Loading...')}</div>

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">{t('Payslip','Payslip')}</h2>
        <div className="flex gap-2">
          <Button onClick={()=> window.print()}>{t('Print','Print')}</Button>
          <Button onClick={()=> { navigator.clipboard.writeText(window.location.href); toast.success(t('Link copied') || 'Link copied') }}>{t('Copy Link','Copy Link')}</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{payslip.name}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-muted-foreground">{t('Period','Period')}</div>
              <div className="font-semibold">{payslip.period}</div>
            </div>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">{t('Net','Net')}</div>
              <div className="font-semibold">{new Intl.NumberFormat(i18n.language === 'fa' ? 'fa-IR' : 'en-US', { style:'currency', currency:'IRR', maximumFractionDigits:0 }).format(payslip.net)}</div>
            </div>
          </div>

          <div className="mt-4">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left"><th className="p-2">{t('Item','Item')}</th><th className="p-2">{t('Amount','Amount')}</th></tr>
              </thead>
              <tbody>
                {payslip.details.map((d:any, idx:number)=> (
                  <tr key={idx} className="border-t"><td className="p-2">{d.name || d.code}</td><td className="p-2 text-right">{new Intl.NumberFormat(i18n.language === 'fa' ? 'fa-IR' : 'en-US', { style:'currency', currency:'IRR', maximumFractionDigits:0 }).format(Number(d.amount||0))}</td></tr>
                ))}
              </tbody>
            </table>
          </div>

        </CardContent>
      </Card>
    </div>
  )
}
