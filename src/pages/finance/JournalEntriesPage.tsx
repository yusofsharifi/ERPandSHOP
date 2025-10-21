import React, { useEffect, useState } from 'react'
import { API_BASE_URL } from '@/lib/utils'
import { Button } from '@/components/ui/Button'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'

import ImportModal from '@/components/finance/ImportModal'
import toast from 'react-hot-toast'

export default function JournalEntriesPage(){
  const { t } = useTranslation()
  const [items, setItems] = useState<any[]>([])
  const [importOpen, setImportOpen] = useState(false)
  const navigate = useNavigate()

  const fetchList = async ()=>{
    const res = await fetch(`${API_BASE_URL}/api/v1/finance/journal-entries?per_page=50&company_id=00000000-0000-0000-0000-000000000000`)
    const d = await res.json()
    setItems(d.items || [])
  }

  useEffect(()=>{ fetchList() }, [])

  const exportEntry = async (id:string)=>{
    try{
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/journal-entries/${id}/export`, { headers: {'X-User-Id':'admin@local'} })
      if(!res.ok){ const d=await res.json(); toast.error(d?.detail?.message?.fa || d?.detail?.message?.en || 'Export failed'); return }
      const text = await res.text()
      const blob = new Blob([text], { type: 'text/csv' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `journal_${id}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    }catch(e){ toast.error('Export error') }
  }

  return (
    <div className="p-4 space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">{t('finance.journal_list') || 'Journal Entries'}</h2>
        <div className="flex gap-2">
          <Button onClick={()=> navigate('/finance/journal-entries/new')}>{t('New') || 'New'}</Button>
          <Button onClick={()=> setImportOpen(true)}>Import</Button>
          <Button variant="outline" onClick={()=> window.location.reload()}>Refresh</Button>
        </div>
      </div>

      <table className="w-full table-auto">
        <thead><tr><th>#</th><th>Number</th><th>Date</th><th>Description</th><th>Debit</th><th>Credit</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {items.map((it:any)=>(
            <tr key={it.id} className="border-t">
              <td className="p-2">{it.id}</td>
              <td className="p-2">{it.number ?? '—'}</td>
              <td className="p-2">{it.date}</td>
              <td className="p-2">{it.description}</td>
              <td className="p-2">{it.total_debit}</td>
              <td className="p-2">{it.total_credit}</td>
              <td className="p-2">{it.status}</td>
              <td className="p-2 flex gap-2"><Button size="sm" onClick={()=> navigate(`/finance/journal-entries/${it.id}`)}>View</Button><Button size="sm" variant="ghost" onClick={()=> exportEntry(it.id)}>Export</Button></td>
            </tr>
          ))}
        </tbody>
      </table>

      <ImportModal open={importOpen} onClose={()=> setImportOpen(false)} />
    </div>
  )
}
