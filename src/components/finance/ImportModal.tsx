import React, { useState } from 'react'
import { Button } from '@/components/ui/Button'
import { API_BASE_URL } from '@/lib/utils'
import toast from 'react-hot-toast'

export default function ImportModal({ open, onClose }:{ open:boolean; onClose:()=>void }){
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<any>(null)
  const [errors, setErrors] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  if(!open) return null

  const doPreview = async (commit=false) => {
    if(!file) { toast.error('Select a file'); return }
    setLoading(true)
    const fd = new FormData()
    fd.append('file', file)
    try{
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/journal-entries/import?dry_run=${!commit}`, { method: 'POST', headers: {'X-User-Id':'admin@local'}, body: fd })
      const d = await res.json()
      if(!res.ok){ toast.error(d?.detail?.message?.fa || d?.detail?.message?.en || 'Import failed'); setLoading(false); return }
      if(commit){ toast.success('Imported'); onClose(); }
      else { setPreview(d.result); setErrors(d.result.errors || []) }
    }catch(e){ toast.error('Import error') }
    setLoading(false)
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-card p-4 rounded w-full max-w-2xl">
        <h3 className="text-lg font-bold">Import Journal Entries (CSV)</h3>
        <p className="text-sm mt-1">CSV must include columns: entry_ref, company_id, fiscal_year, period, date, description, account_id, debit, credit</p>
        <input className="mt-3" type="file" accept=".csv" onChange={(e:any)=> setFile(e.target.files?.[0]||null)} />
        <div className="mt-3 flex gap-2">
          <Button onClick={()=> doPreview(false)} disabled={!file || loading}>Preview</Button>
          <Button variant="secondary" onClick={()=> doPreview(true)} disabled={!file || loading}>Import (Commit)</Button>
          <Button variant="outline" onClick={onClose}>Close</Button>
        </div>
        {preview && (
          <div className="mt-4 max-h-64 overflow-auto">
            <h4 className="font-medium">Preview</h4>
            <pre className="text-xs bg-muted p-2 rounded">{JSON.stringify(preview, null, 2)}</pre>
          </div>
        )}
        {errors && errors.length>0 && (
          <div className="mt-2 text-sm text-red-600">Errors: {errors.length}</div>
        )}
      </div>
    </div>
  )
}
