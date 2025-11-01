import React, { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

export default function ReconciliationPage(){
  const { t, i18n } = useTranslation()
  const [file, setFile] = useState<File | null>(null)
  const [mapping, setMapping] = useState({ date: 'date', description: 'description', amount: 'amount', reference: 'reference' })
  const [draft, setDraft] = useState<any>({ bank_lines: [], system_candidates: [], suggestions: [] })

  const upload = async () => {
    if (!file) return toast.error(t('treasury.upload_statement'))
    const fd = new FormData(); fd.append('file', file)
    const res = await fetch('/api/treasury/reconciliation/upload', { method: 'POST', body: fd })
    if (!res.ok) return toast.error(t('error'))
    const data = await res.json()
    toast.success(t('success'))
    // fetch draft - for simplicity parse client-side
    // We'll just set draft.bank_lines length
    setDraft({ bank_lines: new Array(data.imported||0).fill({}), system_candidates: [], suggestions: [] })
  }

  const runMatch = async () => {
    // placeholder: call API
    const res = await fetch('/api/treasury/reconciliation/0000/match', { method: 'POST' })
    if (!res.ok) return toast.error(t('error'))
    const data = await res.json()
    setDraft(prev => ({ ...prev, suggestions: data.suggestions || [] }))
  }

  const apply = async () => {
    const res = await fetch('/api/treasury/reconciliation/0000/apply', { method: 'POST' })
    if (!res.ok) return toast.error(t('error'))
    toast.success(t('treasury.apply'))
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
              <h4 className="font-semibold mb-2">{t('treasury.upload_statement')}</h4>
              <div className="space-y-2">
                {draft.bank_lines.map((l:any, idx:number)=> (
                  <div key={idx} className="p-2 border rounded">{l.statement_date || '—'} — {l.description || '—'} — {l.amount || '—'}</div>
                ))}
                {draft.bank_lines.length === 0 && <div className="text-sm text-muted">No bank lines</div>}
              </div>
            </div>
            <div>
              <h4 className="font-semibold mb-2">{t('treasury.matches')}</h4>
              <div className="space-y-2">
                {draft.suggestions.map((s:any, idx:number)=> (
                  <div key={idx} className="p-2 border rounded">Suggestion {idx+1}</div>
                ))}
                {draft.suggestions.length === 0 && <div className="text-sm text-muted">No suggestions</div>}
              </div>
            </div>
          </div>

        </CardContent>
      </Card>
    </div>
  )
}
