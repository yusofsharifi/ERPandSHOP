import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

export default function ReconciliationPage(){
  const { t, i18n } = useTranslation()
  const { user } = useAuth()
  const canApply = user && (user.role === 'Admin' || String(user.role).toLowerCase().includes('treasury'))
  const [file, setFile] = useState<File | null>(null)
  const [mapping, setMapping] = useState({ date: 'date', description: 'description', amount: 'amount', reference: 'reference' })
  const [draft, setDraft] = useState<any>({ id: null, bank_lines: [], system_candidates: [], suggestions: [], matches: {} })

  // client-side file parse for offline
  const parseLocal = (f: File) => {
    const reader = new FileReader()
    reader.onload = () => {
      const text = String(reader.result || '')
      const lines = (window as any).backendParsers ? (window as any).backendParsers.parse_statement(text) : (window as any).Papa ? (window as any).Papa.parse(text, { header: true }).data : []
      // normalize
      const bl = lines.map((l:any, idx:number)=> ({ id: 'b-'+idx, statement_date: l.statement_date, description: l.description, amount: l.amount, reference: l.reference }))
      setDraft(prev => ({ ...prev, bank_lines: bl }))
    }
    reader.readAsText(f)
  }

  const upload = async () => {
    if (!file) return toast.error(t('treasury.upload_statement'))
    // offline parse first
    parseLocal(file)
    const fd = new FormData(); fd.append('file', file); fd.append('bank_account_id','00000000-0000-0000-0000-000000000000')
    const res = await fetch('/api/treasury/reconciliation/upload', { method: 'POST', body: fd, headers: {'X-User-Id': user?.id || '' , 'X-Company-Id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'} })
    if (!res.ok) return toast.error(t('error'))
    const data = await res.json()
    toast.success(t('success'))
    // fetch draft from server
    const reconRes = await fetch(`/api/treasury/reconciliation/${data.reconciliation_id}`)
    if (reconRes.ok){
      const json = await reconRes.json()
      setDraft(prev => ({ ...prev, id: json.id }))
    }
  }

  const runMatch = async () => {
    if (!draft.id) return toast.error('No draft')
    const res = await fetch(`/api/treasury/reconciliation/${draft.id}/match`, { method: 'POST' })
    if (!res.ok) return toast.error(t('error'))
    const data = await res.json()
    setDraft(prev => ({ ...prev, suggestions: data.suggestions || [] }))
  }

  const apply = async () => {
    if (!canApply) return toast.error(t('treasury.permission_denied'))
    if (!draft.id) return toast.error('No draft')
    const res = await fetch(`/api/treasury/reconciliation/${draft.id}/apply`, { method: 'POST', headers: {'X-User-Id': user?.id || ''} })
    if (!res.ok) return toast.error(t('error'))
    const data = await res.json()
    toast.success(t('treasury.apply'))
    // show preview
    console.log('applied', data)
  }

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('treasury.upload_statement')}</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('treasury.upload_statement')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <input type="file" accept=".csv,.txt" onChange={(e:any)=> setFile(e.target.files?.[0] || null)} />
            <div className="mt-2 flex gap-2">
              <Button onClick={upload}>{t('treasury.upload_statement')}</Button>
              <Button onClick={runMatch}>{t('treasury.suggest_matches')}</Button>
              <Button variant="outline" onClick={apply}>{t('treasury.apply')}</Button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-semibold mb-2">Bank statement</h4>
              <div className="space-y-2">
                {draft.bank_lines.map((l:any, idx:number)=> (
                  <div key={l.id} draggable className="p-2 border rounded" onDragStart={(e)=> e.dataTransfer?.setData('text/plain', l.id)}>
                    <div className="flex justify-between"><div>{l.statement_date || '—'} — {l.description || '—'}</div><div>{l.amount || '—'}</div></div>
                  </div>
                ))}
                {draft.bank_lines.length === 0 && <div className="text-sm text-muted">No bank lines</div>}
              </div>
              <div className="mt-3">
                <Button onClick={()=> exportReconciliationDraft(draft)}>{t('treasury.export')}</Button>
                <Button variant="outline" onClick={()=> previewReconciliation(draft)}>{t('treasury.preview')}</Button>
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-2">System transactions (drop bank line here to match)</h4>
              <div onDragOver={(e)=> e.preventDefault()} onDrop={(e)=> handleDrop(e)} className="min-h-40 p-2 border rounded">
                {draft.system_candidates.map((s:any, idx:number)=> (
                  <div key={s.id} className="p-2 border rounded mb-2">
                    <div className="flex justify-between"><div>{s.date} — {s.description}</div><div>{s.amount}</div></div>
                    <div className="mt-1 text-sm text-muted">Matches: {(Object.values(draft.matches || {}) as any[]).filter(m=> m.txn_id === s.id).length}</div>
                  </div>
                ))}
                {draft.system_candidates.length === 0 && <div className="text-sm text-muted">No system transactions</div>}
              </div>

              <div className="mt-3">
                {draft.suggestions.map((s:any, idx:number)=> (
                  <div key={idx} className="p-2 border rounded mb-2 flex justify-between items-center">
                    <div>{s.line.statement_date} — {s.line.description} — {s.line.amount}</div>
                    <div className="text-sm px-2 py-1 rounded bg-slate-100">Confidence: {s.score}</div>
                    <div><Button size="sm" onClick={()=> applySuggestion(s)}>{t('apply')}</Button></div>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </CardContent>
      </Card>
    </div>
  )
}
