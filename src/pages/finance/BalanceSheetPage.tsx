import React, { useEffect, useState } from 'react'
import { API_BASE_URL } from '@/lib/utils'

import { useTranslation } from 'react-i18next'

export default function BalanceSheetPage(){
  const { t } = useTranslation()
  const [rows, setRows] = useState<any[]>([])
  useEffect(()=>{ (async ()=>{
    try{
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/reports/balance-sheet?company_id=00000000-0000-0000-0000-000000000000`)
      if(!res.ok) throw new Error('Failed')
      const d = await res.json()
      setRows(d.items || [])
    }catch(e){
      // fallback mock
      setRows([
        { group: 'Assets', account: 'Cash', amount: 10000 },
        { group: 'Liabilities', account: 'Bank Loan', amount: 4000 },
        { group: 'Equity', account: 'Owner Equity', amount: 6000 },
      ])
    }
  })() }, [])

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold">{t('finance.balance_sheet') || 'Balance Sheet'}</h2>
      <div className="mt-3">
        <table className="w-full table-auto"><thead><tr><th>Group</th><th>Account</th><th className="text-right">Amount</th></tr></thead>
          <tbody>
            {rows.map((r, idx)=> (<tr key={idx} className="border-t"><td className="p-2">{r.group}</td><td className="p-2">{r.account}</td><td className="p-2 text-right">{Number(r.amount).toFixed(2)}</td></tr>))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
