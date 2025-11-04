import React, { useEffect, useState } from 'react'
import { API_BASE_URL } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import ChartOfAccounts from '@/components/finance/ChartOfAccounts'

export default function AccountsPage(){
  const [accounts, setAccounts] = useState<any[]>([])
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({ company_id: '00000000-0000-0000-0000-000000000000', code:'', name:'', type:'asset', currency:'IRR', status:'active', description:'', parent_code: '' })

  const fetchAccounts = async ()=>{
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/accounts?company_id=${form.company_id}&per_page=200`)
      if (!res.ok) throw new Error('Network response was not ok')
      const d = await res.json()
      setAccounts(d.items || [])
    } catch (err) {
      console.warn('Failed to fetch accounts, using fallback mock data', err)
      const mock = [
        { id: 'acc-1', code: '1', name: 'Assets', type: 'asset', currency:'IRR', status:'active' },
        { id: 'acc-1.1', code: '1.1', name: 'Cash', type: 'asset', currency:'IRR', status:'active' },
        { id: 'acc-2', code: '2', name: 'Liabilities', type: 'liability', currency:'IRR', status:'active' },
      ]
      setAccounts(mock)
    }
  }
  useEffect(()=>{ fetchAccounts() }, [])

  const create = async ()=>{
    try {
      const payload = { ...form }
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/accounts`, { method:'POST', headers:{'Content-Type':'application/json','X-User-Id':'admin@local'}, body: JSON.stringify(payload) })
      if (!res.ok) throw new Error('Failed to create account')
      setShowForm(false)
      fetchAccounts()
    } catch (err) {
      console.warn('Create account API failed, adding locally', err)
      const newAcc = { id: `mock-${Date.now()}`, code: form.code || '0000', name: form.name || 'New Account', type: form.type, currency: form.currency, status: form.status, description: form.description }
      setAccounts(prev => [newAcc, ...prev])
      setShowForm(false)
    }
  }

  const toggleDisable = (id:string)=>{
    setAccounts(prev => prev.map(a=> a.id === id ? { ...a, disabled: !a.disabled } : a))
  }

  const editAccount = (id:string)=>{
    const a = accounts.find(ac=> ac.id === id)
    if(!a) return
    setForm({ company_id: a.company_id || form.company_id, code: a.code||'', name: a.name||'', type: a.type||'asset', currency: a.currency||'IRR', status: a.status||'active', description: a.description||'', parent_code: '' })
    setShowForm(true)
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold">Chart of Accounts</h2>
        <div>
          <Button onClick={()=> setShowForm(true)}>Add Account</Button>
        </div>
      </div>

      {showForm && (
        <div className="p-3 border rounded bg-card mb-4">
          <div className="grid grid-cols-3 gap-2">
            <input className="input" placeholder="Code (e.g. 1, 1.1)" value={form.code} onChange={(e)=> setForm({...form, code: e.target.value})} />
            <input className="input" placeholder="Name" value={form.name} onChange={(e)=> setForm({...form, name: e.target.value})} />
            <select className="input" value={form.type} onChange={(e)=> setForm({...form, type: e.target.value})}><option value="asset">Asset</option><option value="liability">Liability</option><option value="equity">Equity</option><option value="revenue">Revenue</option><option value="expense">Expense</option></select>
            <input className="input" placeholder="Currency" value={form.currency} onChange={(e)=> setForm({...form, currency: e.target.value})} />
            <select className="input" value={form.status} onChange={(e)=> setForm({...form, status: e.target.value})}><option value="active">Active</option><option value="suspended">Suspended</option><option value="closed">Closed</option></select>
            <input className="input" placeholder="Parent code (optional)" value={form.parent_code} onChange={(e)=> setForm({...form, parent_code: e.target.value})} />
            <textarea className="input col-span-3 h-24" placeholder="Description" value={form.description} onChange={(e)=> setForm({...form, description: e.target.value})} />
          </div>
          <div className="mt-3 flex gap-2"><Button onClick={create}>Save</Button><Button variant="outline" onClick={()=> setShowForm(false)}>Cancel</Button></div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <ChartOfAccounts accounts={accounts} onToggle={toggleDisable} onEdit={editAccount} />
        </div>
        <div>
          <h3 className="text-sm font-semibold mb-2">Accounts list</h3>
          <div className="overflow-auto border rounded bg-card p-2 max-h-96">
            <table className="w-full table-auto">
              <thead><tr><th className="p-1 text-left">Code</th><th className="p-1 text-left">Name</th><th className="p-1">Type</th><th className="p-1">Status</th></tr></thead>
              <tbody>
                {accounts.map(a=> (
                  <tr key={a.id} className="border-t"><td className="p-1 align-top">{a.code}</td><td className="p-1 align-top">{a.name}</td><td className="p-1 align-top">{a.type}</td><td className="p-1 align-top">{a.status || (a.disabled ? 'Disabled' : 'Active')}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
