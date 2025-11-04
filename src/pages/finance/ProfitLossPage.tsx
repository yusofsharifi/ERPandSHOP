import React, { useEffect, useState } from 'react'
import { API_BASE_URL } from '@/lib/utils'

export default function ProfitLossPage(){
  const [rows, setRows] = useState<any[]>([])
  useEffect(()=>{ (async ()=>{
    try{
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/reports/profit-and-loss?company_id=00000000-0000-0000-0000-000000000000`)
      if(!res.ok) throw new Error('Failed')
      const d = await res.json()
      setRows(d.items || [])
    }catch(e){
      setRows([
        { group: 'Revenue', account: 'Sales', amount: 15000 },
        { group: 'Expenses', account: 'COGS', amount: -8000 },
        { group: 'Expenses', account: 'Salaries', amount: -3000 },
      ])
    }
  })() }, [])

  const total = rows.reduce((s,r)=> s + Number(r.amount||0), 0)

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold">Profit & Loss</h2>
      <div className="mt-3">
        <table className="w-full table-auto"><thead><tr><th>Group</th><th>Account</th><th className="text-right">Amount</th></tr></thead>
          <tbody>
            {rows.map((r, idx)=> (<tr key={idx} className="border-t"><td className="p-2">{r.group}</td><td className="p-2">{r.account}</td><td className="p-2 text-right">{Number(r.amount).toFixed(2)}</td></tr>))}
            <tr className="border-t font-semibold"><td colSpan={2} className="p-2">Net</td><td className="p-2 text-right">{total.toFixed(2)}</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
