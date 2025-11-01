import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import PayslipModal from '@/components/hr/PayslipModal'

type Employee = {
  id: string
  company_id?: string
  employee_code?: string
  first_name: string
  last_name: string
  job_title?: string
  department_id?: string
  base_salary?: number
  is_active?: boolean
}

export default function PayrollEmployeesPage(){
  const { t, i18n } = useTranslation()
  const [employees, setEmployees] = useState<Employee[]>([])
  const [query, setQuery] = useState('')
  const [openPayslip, setOpenPayslip] = useState(false)
  const [selected, setSelected] = useState<any | null>(null)

  const fetchEmployees = async ()=>{
    try{
      const res = await fetch('/api/payroll/employees')
      if(!res.ok) throw new Error('failed')
      const data = await res.json()
      setEmployees(data)
    }catch(e){ console.error(e); toast.error(i18n.language === 'fa' ? 'خطا در دریافت پرسنل' : 'Failed to load employees') }
  }

  useEffect(()=>{ fetchEmployees() }, [])

  const filtered = employees.filter(e => (
    `${e.first_name} ${e.last_name}`.toLowerCase().includes(query.toLowerCase()) || (e.job_title||'').toLowerCase().includes(query.toLowerCase())
  ))

  const viewPayslip = (emp:any)=>{
    setSelected({ id: emp.id, name: `${emp.first_name} ${emp.last_name}`, gross: emp.base_salary || 0, tax: 0, net: emp.base_salary || 0, period: '' })
    setOpenPayslip(true)
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">{t('hr.employees','Employees')}</h2>
        <div className="flex gap-2">
          <input className="input" placeholder={t('search','Search')} value={query} onChange={(e)=> setQuery(e.target.value)} />
          <Button onClick={fetchEmployees}>{t('Refresh','Refresh')}</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('hr.employee_directory','Employee Directory')}</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full table-auto">
            <thead>
              <tr className="text-left"><th className="p-2">{t('Name','Name')}</th><th className="p-2">{t('Job Title','Job Title')}</th><th className="p-2">{t('Salary','Salary')}</th><th className="p-2">{t('Status','Status')}</th><th className="p-2">{t('Actions','Actions')}</th></tr>
            </thead>
            <tbody>
              {filtered.map(e=> (
                <tr key={e.id} className="border-t">
                  <td className="p-2">{e.first_name} {e.last_name}</td>
                  <td className="p-2">{e.job_title}</td>
                  <td className="p-2">{new Intl.NumberFormat(i18n.language === 'fa' ? 'fa-IR' : 'en-US', { style:'currency', currency:'IRR', maximumFractionDigits:0 }).format(e.base_salary || 0)}</td>
                  <td className="p-2">{e.is_active ? t('Active','Active') : t('Inactive','Inactive')}</td>
                  <td className="p-2 flex gap-2">
                    <Button size="sm" onClick={()=> window.location.href = `/hr/payroll/${e.id}/payslip`}>{t('View Payslip','View Payslip')}</Button>
                    <Button size="sm" variant="outline" onClick={()=> viewPayslip(e)}>{t('Quick View','Quick View')}</Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <PayslipModal open={openPayslip} onOpenChange={setOpenPayslip} payslip={selected} />
    </div>
  )
}
