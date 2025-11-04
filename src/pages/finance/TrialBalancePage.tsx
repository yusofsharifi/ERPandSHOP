import React, { useEffect, useState } from 'react'
import { API_BASE_URL } from '@/lib/utils'

import { useTranslation } from 'react-i18next'

export default function TrialBalancePage(){
  const { t } = useTranslation()
  const [rows, setRows] = useState<any[]>([])
  useEffect(()=>{ (async ()=>{ const res = await fetch(`${API_BASE_URL}/api/v1/finance/reports/trial-balance?company_id=00000000-0000-0000-0000-000000000000`); const d = await res.json(); setRows(d.items || []) })() }, [])
  return (
    <div className="p-4">
      <h2 className="text-lg font-bold">{t('finance.trial_balance') || 'Trial Balance'}</h2>
      <table className="w-full table-auto mt-3"><thead><tr><th>Account</th><th>Debit</th><th>Credit</th></tr></thead>
        <tbody>
          {rows.map(r=> (<tr key={r.account_id} className="border-t"><td className="p-2">{r.account_id}</td><td className="p-2">{r.debit}</td><td className="p-2">{r.credit}</td></tr>))}
        </tbody>
      </table>
    </div>
  )
}
