import React, { useState, useMemo, useEffect } from 'react'
import React, { useState, useEffect, useMemo } from 'react'
import JournalLinesTable from '@/components/finance/JournalLinesTable'
import TotalsBar from '@/components/finance/TotalsBar'
import PostConfirmationModal from '@/components/finance/PostConfirmationModal'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'
import { API_BASE_URL } from '@/lib/utils'
import toast from 'react-hot-toast'
import CustomerLookup from '@/components/invoices/CustomerLookup'
import AccountSelect from '@/components/finance/AccountSelect'

export default function JournalEntryNewPage(){
  const { t } = useTranslation()
  const [lines, setLines] = useState<any[]>([{ line_no:1, account_id:'', description:'', debit:0, credit:0 }])
  const [date, setDate] = useState(new Date().toISOString().slice(0,10))
  const [description, setDescription] = useState('')
  const [fiscalYear, setFiscalYear] = useState(new Date().getFullYear())
  const [companyId, setCompanyId] = useState('00000000-0000-0000-0000-000000000000')
  const [reference, setReference] = useState('')
  const [documentType, setDocumentType] = useState('journal')
  const [currency, setCurrency] = useState('USD')
  const [exchangeRate, setExchangeRate] = useState(1)
  const [partnerId, setPartnerId] = useState<string | null>(null)
  const [partnerName, setPartnerName] = useState<string | null>(null)
  const [taxAmount, setTaxAmount] = useState<number>(0)
  const [costCenter, setCostCenter] = useState('')
  const [project, setProject] = useState('')
  const [department, setDepartment] = useState('')
  const [approvalRequired, setApprovalRequired] = useState(false)
  const [internalNotes, setInternalNotes] = useState('')
  const totals = useMemo(()=> ({ totalDebit: lines.reduce((s,l)=> s + (Number(l.debit||0)),0), totalCredit: lines.reduce((s,l)=> s + (Number(l.credit||0)),0) }), [lines])
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [preview, setPreview] = useState<any>(null)
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null)
  const [entryId, setEntryId] = useState<string | null>(null)
  const [lockInfo, setLockInfo] = useState<{locked_by?: string, locked_at?: string} | null>(null)

  useEffect(()=>{
    const handler = (e:KeyboardEvent)=>{
      if((e.ctrlKey||e.metaKey)&& e.key==='s'){ e.preventDefault(); saveDraft(); }
      if((e.ctrlKey||e.metaKey)&& e.key==='p'){ e.preventDefault(); openPost() }
    }
    window.addEventListener('keydown', handler)
    return ()=> window.removeEventListener('keydown', handler)
  }, [lines, date, description])

  const saveDraft = async ()=>{
    try{
      const payload = { company_id: '00000000-0000-0000-0000-000000000000', fiscal_year: fiscalYear, period: `${fiscalYear}-${String(new Date(date).getMonth()+1).padStart(2,'0')}`, date, description, lines }
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/journal-entries`, { method: 'POST', headers: {'Content-Type':'application/json','X-User-Id':'admin@local'}, body: JSON.stringify(payload) })
      if(!res.ok){ const d = await res.json(); toast.error(d?.detail?.message?.fa || d?.detail?.message?.en || 'Error') ; return }
      const data = await res.json()
      toast.success(t('gl.success.entry_saved') || 'Saved')

      // upload attachments if any
      if(selectedFiles && selectedFiles.length > 0){
        for(let i=0;i<selectedFiles.length;i++){
          const f = selectedFiles[i]
          const fd = new FormData()
          fd.append('file', f)
          try{
            const r = await fetch(`${API_BASE_URL}/api/v1/finance/journal-entries/${data.id}/attachments`, { method: 'POST', headers: {'X-User-Id':'admin@local'}, body: fd })
            if(r.ok){ toast.success('Attachment uploaded') } else { const dd = await r.json(); toast.error(dd?.detail?.message?.fa || dd?.detail?.message?.en || 'Attach failed') }
          }catch(e){ toast.error('Attach error') }
        }
      }

      // set entry id for further actions
      if(data && data.id){ setEntryId(data.id) }
      return data
    }catch(e){ toast.error('Error saving') }
  }

  const lockEntry = async ()=>{
    if(!entryId){ toast.error('Save draft first to lock'); return }
    try{
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/journal-entries/${entryId}/lock`, { method: 'POST', headers: {'X-User-Id':'admin@local'} })
      if(!res.ok){ const d = await res.json(); toast.error(d?.detail?.message?.fa || d?.detail?.message?.en || 'Lock failed'); return }
      const d = await res.json()
      setLockInfo(d.lock)
      toast.success('Locked')
    }catch(e){ toast.error('Lock error') }
  }

  const unlockEntry = async ()=>{
    if(!entryId){ toast.error('No entry'); return }
    try{
      const res = await fetch(`${API_BASE_URL}/api/v1/finance/journal-entries/${entryId}/unlock`, { method: 'POST', headers: {'X-User-Id':'admin@local'} })
      if(!res.ok){ const d = await res.json(); toast.error(d?.detail?.message?.fa || d?.detail?.message?.en || 'Unlock failed'); return }
      const d = await res.json()
      setLockInfo(null)
      toast.success('Unlocked')
    }catch(e){ toast.error('Unlock error') }
  }

  const openPost = async ()=>{
    if(Number(totals.totalDebit.toFixed(2)) !== Number(totals.totalCredit.toFixed(2))){ toast.error(t('gl.error.not_balanced') || 'Not balanced'); return }
    // preview next number (in-memory backend cannot predict global number; show placeholder)
    setPreview({ number: 'preview', date })
    setConfirmOpen(true)
  }

  const doPost = async ()=>{
    setConfirmOpen(false)
    const draft = await saveDraft()
    if(!draft || !draft.id) return
    const res = await fetch(`${API_BASE_URL}/api/v1/finance/journal-entries/${draft.id}/post`, { method: 'POST', headers: {'X-User-Id':'admin@local','X-User-Roles':'finance_post'} })
    if(!res.ok){ const d=await res.json(); toast.error(d?.detail?.message?.fa || d?.detail?.message?.en||'Post failed'); return }
    const d = await res.json()
    toast.success(d?.message?.fa || d?.message?.en || 'Posted')
  }

  return (
    <div className="space-y-4 p-4">
      <h2 className="text-xl font-bold">{t('finance.journal_new') || 'New Journal Entry'}</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
        <div>
          <label className="text-sm">{t('gl.labels.date') || 'Date'}</label>
          <input type="date" value={date} onChange={(e)=> setDate(e.target.value)} className="input" />
        </div>
        <div>
          <label className="text-sm">Fiscal Year</label>
          <input type="number" value={fiscalYear} onChange={(e)=> setFiscalYear(Number(e.target.value))} className="input" />
        </div>
        <div>
          <label className="text-sm">Reference No</label>
          <input value={reference} onChange={(e)=> setReference(e.target.value)} className="input" />
        </div>

        <div>
          <label className="text-sm">Document Type</label>
          <select value={documentType} onChange={(e)=> setDocumentType(e.target.value)} className="input">
            <option value="journal">Journal</option>
            <option value="adjustment">Adjustment</option>
            <option value="reversal">Reversal</option>
          </select>
        </div>

        <div>
          <label className="text-sm">Currency</label>
          <select value={currency} onChange={(e)=> setCurrency(e.target.value)} className="input">
            <option>USD</option>
            <option>EUR</option>
            <option>IRR</option>
          </select>
        </div>

        <div>
          <label className="text-sm">Exchange Rate</label>
          <input type="number" value={exchangeRate} onChange={(e)=> setExchangeRate(Number(e.target.value))} className="input" />
        </div>

        <div className="md:col-span-2">
          <label className="text-sm">Partner (Customer / Vendor)</label>
          <CustomerLookup onSelect={(id,name)=> { setPartnerId(id); setPartnerName(name) }} />
          {partnerName && <div className="text-sm mt-1">Selected: {partnerName}</div>}
        </div>

        <div>
          <label className="text-sm">Tax Amount</label>
          <input type="number" value={taxAmount} onChange={(e)=> setTaxAmount(Number(e.target.value))} className="input" />
        </div>

        <div>
          <label className="text-sm">Cost Center</label>
          <input value={costCenter} onChange={(e)=> setCostCenter(e.target.value)} className="input" />
        </div>

        <div>
          <label className="text-sm">Project</label>
          <input value={project} onChange={(e)=> setProject(e.target.value)} className="input" />
        </div>

        <div>
          <label className="text-sm">Department</label>
          <input value={department} onChange={(e)=> setDepartment(e.target.value)} className="input" />
        </div>

        <div className="md:col-span-3">
          <label className="text-sm">Internal Notes</label>
          <textarea value={internalNotes} onChange={(e)=> setInternalNotes(e.target.value)} className="input h-24" />
        </div>
      </div>

      <JournalLinesTable lines={lines} setLines={setLines} />

      <div className="p-2 border rounded bg-card">
        <label className="text-sm">Attachments</label>
        <input type="file" multiple onChange={(e:any)=> setSelectedFiles(e.target.files)} />
      </div>

      <div className="flex justify-between items-center">
        <div>
          {entryId ? (
            <div className="flex items-center gap-2">
              <div className="text-sm">{lockInfo ? `Locked by: ${lockInfo.locked_by || 'you'}` : 'Unlocked'}</div>
              {lockInfo ? (
                <Button size="sm" variant="outline" onClick={unlockEntry}>Unlock</Button>
              ) : (
                <Button size="sm" variant="outline" onClick={lockEntry}>Lock</Button>
              )}
            </div>
          ) : null}
        </div>
        <div className="flex gap-2">
          <Button variant="default" onClick={()=> saveDraft()}>{t('save') || 'Save'}</Button>
          <Button variant="secondary" onClick={openPost} disabled={lines.length < 2 || Number(totals.totalDebit.toFixed(2)) !== Number(totals.totalCredit.toFixed(2))}>{t('Post') || 'Post'}</Button>
        </div>
      </div>

      <TotalsBar totalDebit={totals.totalDebit} totalCredit={totals.totalCredit} />

      <PostConfirmationModal open={confirmOpen} onClose={()=> setConfirmOpen(false)} onConfirm={doPost} preview={preview} />
    </div>
  )
}
