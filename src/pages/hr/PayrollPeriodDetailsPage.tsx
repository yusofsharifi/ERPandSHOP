import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'

type Row = { id:string, employee:string, gross:number, deductions:number, net:number, payment_status:string }

export default function PayrollPeriodDetailsPage(){
  const { period_id } = useParams()
  const { t, i18n } = useTranslation()
  const [rows, setRows] = useState<Row[]>([])
  const [query, setQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const fetchRows = async ()=>{
    try{
      const res = await fetch(`/api/payroll/report?period_id=${period_id}`)
      if(!res.ok) throw new Error('failed')
      const data = await res.json()
      // map report rows to visible rows (mock)
      const mapped = (data.rows || []).map((r:any, idx:number)=> ({ id: String(idx+1), employee: r.key, gross: Number(r.gross||0), deductions: Number(r.deductions||0), net: Number(r.net||0), payment_status: 'unpaid' }))
      setRows(mapped)
    }catch(e){ console.error(e); toast.error(i18n.language === 'fa' ? 'خطا در دریافت' : 'Failed to load') }
  }

  useEffect(()=>{ fetchRows() }, [period_id])

  const filtered = rows.filter(r => (r.employee.toLowerCase().includes(query.toLowerCase()) && (statusFilter ? r.payment_status === statusFilter : true)))

  const markPaid = async (id:string)=>{
    try{
      const res = await fetch(`/api/payroll/${id}/pay`, { method: 'POST' })
      if(!res.ok) throw new Error('failed')
      toast.success(i18n.language === 'fa' ? 'پرداخت ثبت شد' : 'Marked as paid')
      fetchRows()
    }catch(e){ console.error(e); toast.error(i18n.language === 'fa' ? 'خطا' : 'Failed') }
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">{t('hr.payroll.period_details','Payroll Period')}</h2>
        <div className="flex gap-2">
          <input className="input" placeholder={t('search','Search')} value={query} onChange={(e)=> setQuery(e.target.value)} />
          <select className="input" value={statusFilter} onChange={(e)=> setStatusFilter(e.target.value)}>
            <option value="">{t('All','All')}</option>
            <option value="unpaid">{t('Unpaid','Unpaid')}</option>
            <option value="in_progress">{t('In Progress','In Progress')}</option>
            <option value="paid">{t('Paid','Paid')}</option>
          </select>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('hr.payroll.payrolls','Payrolls')}</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full table-auto">
            <thead>
              <tr className="text-left"><th className="p-2">{t('Employee','Employee')}</th><th className="p-2">{t('Gross','Gross')}</th><th className="p-2">{t('Deductions','Deductions')}</th><th className="p-2">{t('Net','Net')}</th><th className="p-2">{t('Status','Status')}</th><th className="p-2">{t('Actions','Actions')}</th></tr>
            </thead>
            <tbody>
              {filtered.map(r=> (
                <tr key={r.id} className="border-t"><td className="p-2">{r.employee}</td><td className="p-2">{new Intl.NumberFormat(i18n.language === 'fa' ? 'fa-IR' : 'en-US', { style:'currency', currency:'IRR', maximumFractionDigits:0 }).format(r.gross)}</td><td className="p-2">{r.deductions}</td><td className="p-2">{r.net}</td><td className="p-2">{t(`status.${r.payment_status}`, r.payment_status)}</td><td className="p-2 flex gap-2"><Button size="sm" onClick={()=> fetchRows()}>{t('Validate Payroll','Validate')}</Button><Button size="sm" onClick={()=> markPaid(r.id)}>{t('Mark as Paid','Pay')}</Button></td></tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
