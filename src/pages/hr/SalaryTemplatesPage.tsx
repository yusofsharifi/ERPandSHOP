import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Button } from '@/components/ui/Button'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'

type Template = { id: string, name: string, baseSalary: number }
const STORAGE_KEY = 'hr_salary_templates'

export default function SalaryTemplatesPage(){
  const { t } = useTranslation()
  const [templates, setTemplates] = useState<Template[]>([])
  const [name, setName] = useState('')
  const [base, setBase] = useState(0)

  useEffect(()=>{
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) setTemplates(JSON.parse(raw))
  }, [])

  useEffect(()=>{ localStorage.setItem(STORAGE_KEY, JSON.stringify(templates)) }, [templates])

  const add = ()=>{
    if (!name) return
    const tpls = [{ id: String(Date.now()), name, baseSalary: base }, ...templates]
    setTemplates(tpls)
    setName('')
    setBase(0)
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">{t('Salary Templates','Salary Templates')}</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Templates</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-2 mb-3">
            <input className="input" placeholder="Name" value={name} onChange={(e)=> setName(e.target.value)} />
            <input className="input" placeholder="Base Salary" type="number" value={base} onChange={(e)=> setBase(Number(e.target.value))} />
            <div className="flex gap-2"><Button onClick={add}>Add</Button></div>
          </div>

          <table className="w-full table-auto">
            <thead><tr className="text-left"><th className="p-2">Name</th><th className="p-2">Base Salary</th></tr></thead>
            <tbody>
              {templates.map(tpl=> (
                <tr key={tpl.id} className="border-t"><td className="p-2">{tpl.name}</td><td className="p-2">{tpl.baseSalary}</td></tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>
    </div>
  )
}
