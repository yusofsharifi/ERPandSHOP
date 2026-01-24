import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import PayslipModal from '@/components/hr/PayslipModal'

type PayrollRun = {
  id: string
  name: string
  month: string
  created_at: string
  total: number
  breakdown?: any[]
}

const STORAGE_KEY = 'hr_payroll_runs'

export default function PayrollDetailsPage(){
  const { id } = useParams()
  const { t } = useTranslation()
  const [run, setRun] = useState<PayrollRun | null>(null)
  const [openPayslip, setOpenPayslip] = useState(false)
  const [selected, setSelected] = useState<any | null>(null)

  useEffect(()=>{
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const runs: PayrollRun[] = JSON.parse(raw)
    const found = runs.find(r=> r.id === id) || null
    setRun(found)
  }, [id])

  if (!run) return <div className="p-4">Payroll not found</div>

  const exportDetails = () => {
    const headers = ['Employee ID','Name','Gross','Tax','Net']
    const rows = (run.breakdown || []).map((b:any) => [b.employeeId, b.name, b.gross, b.tax, b.net])
    const csv = [headers, ...rows].map(r => r.map(cell => `"${String(cell).replace(/"/g,'""')}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `payroll_${run.id}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">{run.name} — {run.month}</h2>
        <div className="flex gap-2">
          <Button onClick={exportDetails}>Export to Excel</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Breakdown</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full table-auto">
            <thead>
              <tr className="text-left"><th className="p-2">Employee</th><th className="p-2">Gross</th><th className="p-2">Tax</th><th className="p-2">Net</th><th className="p-2">Actions</th></tr>
            </thead>
            <tbody>
              {(run.breakdown || []).map((b:any)=> (
                <tr key={b.employeeId} className="border-t"><td className="p-2">{b.name}</td><td className="p-2">{b.gross}</td><td className="p-2">{b.tax}</td><td className="p-2">{b.net}</td><td className="p-2"><Button size="sm" onClick={()=>{ setSelected(b); setOpenPayslip(true) }}>View Payslip</Button></td></tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <PayslipModal open={openPayslip} onOpenChange={setOpenPayslip} payslip={selected} />
    </div>
  )
}
