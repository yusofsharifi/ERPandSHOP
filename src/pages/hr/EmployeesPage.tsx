import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'

type Employee = {
  id: string
  name: string
  email: string
  position: string
  salary: number
}

const STORAGE_KEY = 'hr_employees'

export default function EmployeesPage(){
  const { t } = useTranslation()
  const [employees, setEmployees] = useState<Employee[]>([])
  const [query, setQuery] = useState('')

  useEffect(()=>{
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) setEmployees(JSON.parse(raw))
    else {
      const sample: Employee[] = [
        { id: 'e1', name: 'Ali Rezaei', email: 'ali@example.com', position: 'Developer', salary: 5000 },
        { id: 'e2', name: 'Sara Karimi', email: 'sara@example.com', position: 'Designer', salary: 4500 },
        { id: 'e3', name: 'John Doe', email: 'john@example.com', position: 'Accountant', salary: 4800 },
      ]
      setEmployees(sample)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sample))
    }
  }, [])

  useEffect(()=>{ localStorage.setItem(STORAGE_KEY, JSON.stringify(employees)) }, [employees])

  const filtered = employees.filter(e => (
    e.name.toLowerCase().includes(query.toLowerCase()) || e.email.toLowerCase().includes(query.toLowerCase()) || e.position.toLowerCase().includes(query.toLowerCase())
  ))

  const exportToCSV = () => {
    const headers = ['ID','Name','Email','Position','Salary']
    const rows = employees.map(e => [e.id, e.name, e.email, e.position, String(e.salary)])
    const csv = [headers, ...rows].map(r => r.map(cell => `"${String(cell).replace(/"/g,'""')}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'employees.csv'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">{t('hr.employees','Employees')}</h2>
        <div className="flex gap-2">
          <input className="input" placeholder={t('search','Search')} value={query} onChange={(e)=> setQuery(e.target.value)} />
          <Button onClick={exportToCSV}>Export to Excel</Button>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('hr.employee_directory','Employee Directory')}</CardTitle>
        </CardHeader>
        <CardContent>
          <table className="w-full table-auto">
            <thead>
              <tr className="text-left"><th className="p-2">{t('Name','Name')}</th><th className="p-2">{t('Email','Email')}</th><th className="p-2">{t('Position','Position')}</th><th className="p-2">{t('Salary','Salary')}</th></tr>
            </thead>
            <tbody>
              {filtered.map(e=> (
                <tr key={e.id} className="border-t"><td className="p-2">{e.name}</td><td className="p-2">{e.email}</td><td className="p-2">{e.position}</td><td className="p-2">{e.salary}</td></tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
