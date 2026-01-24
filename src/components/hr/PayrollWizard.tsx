import React, { useEffect, useState } from 'react'
import Modal from '@/components/ui/Modal'
import { Button } from '@/components/ui/Button'

type Props = { open: boolean, onOpenChange: (v:boolean)=>void, onCreate: (run:any)=>void }

const EMP_KEY = 'hr_employees'
const RUNS_KEY = 'hr_payroll_runs'

export default function PayrollWizard({ open, onOpenChange, onCreate }: Props){
  const [month, setMonth] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(()=>{
    if (!open) setMonth('')
  }, [open])

  const generate = ()=>{
    setLoading(true)
    const raw = localStorage.getItem(EMP_KEY) || '[]'
    const employees = JSON.parse(raw)
    const taxRate = Number(localStorage.getItem('hr_tax_settings') || '10')
    const breakdown = employees.map((e:any)=>{
      const gross = Number(e.salary || 0)
      const tax = Math.round(gross * taxRate / 100)
      const net = gross - tax
      return { employeeId: e.id, name: e.name, gross, tax, net }
    })
    const total = breakdown.reduce((s:any,b:any)=> s + (b.net||0), 0)
    const run = { id: String(Date.now()), name: `Payroll ${month || new Date().toLocaleDateString()}`, month: month || new Date().toLocaleString(), created_at: new Date().toLocaleString(), total, breakdown }

    const rawRuns = localStorage.getItem(RUNS_KEY)
    const runs = rawRuns ? JSON.parse(rawRuns) : []
    runs.unshift(run)
    localStorage.setItem(RUNS_KEY, JSON.stringify(runs))

    setTimeout(()=>{
      onCreate(run)
      setLoading(false)
      onOpenChange(false)
    }, 400)
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title="Generate Payroll">
      <div className="grid grid-cols-1 gap-3">
        <label>Month</label>
        <input className="input" placeholder="e.g. 2025-08" value={month} onChange={(e)=> setMonth(e.target.value)} />
        <div className="flex gap-2 justify-end">
          <Button variant="outline" onClick={()=> onOpenChange(false)}>Cancel</Button>
          <Button onClick={generate} disabled={loading}>{loading ? 'Generating...' : 'Generate'}</Button>
        </div>
      </div>
    </Modal>
  )
}
