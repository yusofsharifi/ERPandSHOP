import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import PayrollWizard from '@/components/hr/PayrollWizard'
import { useNavigate } from 'react-router-dom'

type PayrollRun = {
  id: string
  name: string
  month: string
  created_at: string
  total: number
}

const STORAGE_KEY = 'hr_payroll_runs'

export default function PayrollPage(){
  const { t } = useTranslation()
  const [runs, setRuns] = useState<PayrollRun[]>([])
  const [openWizard, setOpenWizard] = useState(false)
  const navigate = useNavigate()

  useEffect(()=>{
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) setRuns(JSON.parse(raw))
    else setRuns([])
  }, [])

  useEffect(()=>{ localStorage.setItem(STORAGE_KEY, JSON.stringify(runs)) }, [runs])

  const openRun = (id: string) => { navigate(`/hr/payroll/${id}`) }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">{t('Payroll','Payroll')}</h2>
        <div className="flex gap-2">
          <Button onClick={()=> setOpenWizard(true)}>Generate Payroll</Button>
          <Button variant="outline" onClick={()=>{
            // export runs CSV
            const headers = ['ID','Name','Month','Created At','Total']
            const rows = runs.map(r => [r.id, r.name, r.month, r.created_at, String(r.total)])
            const csv = [headers, ...rows].map(r => r.map(cell => `"${String(cell).replace(/"/g,'""')}"`).join(',')).join('\n')
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = 'payroll_runs.csv'
            a.click()
            URL.revokeObjectURL(url)
          }}>Export to Excel</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Payroll Runs</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full table-auto">
            <thead>
              <tr className="text-left"><th className="p-2">Name</th><th className="p-2">Month</th><th className="p-2">Created</th><th className="p-2">Total</th><th className="p-2">Actions</th></tr>
            </thead>
            <tbody>
              {runs.map(r=> (
                <tr key={r.id} className="border-t"><td className="p-2">{r.name}</td><td className="p-2">{r.month}</td><td className="p-2">{r.created_at}</td><td className="p-2">{r.total}</td><td className="p-2"><Button size="sm" onClick={()=> openRun(r.id)}>View</Button></td></tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <PayrollWizard open={openWizard} onOpenChange={(v)=> setOpenWizard(v)} onCreate={(run)=> setRuns(prev => [run, ...prev])} />
    </div>
  )
}
