import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

export default function ChecksPage(){
  const { t, i18n } = useTranslation()
  const [checks, setChecks] = useState<any[]>([])

  const fetchList = async ()=>{
    try{
      const res = await fetch('/api/treasury/checks')
      if (!res.ok) return setChecks([])
      const data = await res.json()
      setChecks(data)
    }catch(e){ console.error(e) }
  }

  useEffect(()=>{ fetchList() }, [])

  const changeStatus = async (id:string, status:string)=>{
    try{
      const res = await fetch(`/api/treasury/checks/${id}/status`, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({ status }) })
      if (!res.ok) throw new Error('failed')
      toast.success(t('success'))
      fetchList()
    }catch(e){ console.error(e); toast.error(t('error')) }
  }

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Checks</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Checks</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left"><th>Check #</th><th>Bank</th><th>Due</th><th>Amount</th><th>Status</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {checks.map(c=> (
                  <tr key={c.id} className="border-t">
                    <td className="px-2 py-2">{c.check_no}</td>
                    <td className="px-2 py-2">{c.bank_name}</td>
                    <td className="px-2 py-2">{c.due_date}</td>
                    <td className="px-2 py-2">{c.amount}</td>
                    <td className="px-2 py-2">{c.status}</td>
                    <td className="px-2 py-2">
                      <div className="flex gap-2">
                        {c.status !== 'deposited' && <Button size="sm" onClick={()=> changeStatus(c.id, 'deposited')}>Deposit</Button>}
                        {c.status !== 'returned' && <Button size="sm" variant="destructive" onClick={()=> changeStatus(c.id, 'returned')}>Return</Button>}
                      </div>
                    </td>
                  </tr>
                ))}
                {checks.length === 0 && <tr><td colSpan={6} className="p-4 text-center text-sm text-muted">No checks</td></tr>}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
