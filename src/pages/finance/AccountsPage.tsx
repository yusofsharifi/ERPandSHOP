import React, { useEffect, useState } from 'react'
import { API_BASE_URL } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import AccountSelect from '@/components/finance/AccountSelect'

export default function AccountsPage(){
  const [accounts, setAccounts] = useState<any[]>([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ company_id: '00000000-0000-0000-0000-000000000000', code:'', name:'', type:'asset' })

  const fetchAccounts = async ()=>{
    const res = await fetch(`${API_BASE_URL}/api/v1/finance/accounts?company_id=${form.company_id}&per_page=200`)
    const d = await res.json()
    setAccounts(d.items || [])
  }
  useEffect(()=>{ fetchAccounts() }, [])

  const create = async ()=>{
    await fetch(`${API_BASE_URL}/api/v1/finance/accounts`, { method:'POST', headers:{'Content-Type':'application/json','X-User-Id':'admin@local'}, body: JSON.stringify(form) })
    setShowForm(false)
    fetchAccounts()
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">Accounts</h2>
        <div>
          <Button onClick={()=> setShowForm(true)}>Add Account</Button>
        </div>
      </div>
      {showForm && (
        <div className="p-3 border rounded bg-card">
          <div className="grid grid-cols-3 gap-2">
            <input className="input" placeholder="Code" value={form.code} onChange={(e)=> setForm({...form, code: e.target.value})} />
            <input className="input" placeholder="Name" value={form.name} onChange={(e)=> setForm({...form, name: e.target.value})} />
            <select className="input" value={form.type} onChange={(e)=> setForm({...form, type: e.target.value})}><option value="asset">Asset</option><option value="liability">Liability</option><option value="equity">Equity</option><option value="revenue">Revenue</option><option value="expense">Expense</option></select>
          </div>
          <div className="mt-3 flex gap-2"><Button onClick={create}>Save</Button><Button variant="outline" onClick={()=> setShowForm(false)}>Cancel</Button></div>
        </div>
      )}

      <table className="w-full table-auto mt-3">
        <thead><tr><th>Code</th><th>Name</th><th>Type</th><th>Actions</th></tr></thead>
        <tbody>
          {accounts.map(a=> (
            <tr key={a.id} className="border-t"><td className="p-2">{a.code}</td><td className="p-2">{a.name}</td><td className="p-2">{a.type}</td><td className="p-2">—</td></tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
