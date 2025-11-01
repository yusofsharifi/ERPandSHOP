import React, { useEffect, useState, useMemo } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import Modal from '@/components/ui/Modal'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

function useDebounce(val:string, delay=300){
  const [v, setV] = useState(val)
  useEffect(()=>{ const id = setTimeout(()=> setV(val), delay); return ()=> clearTimeout(id) }, [val])
  return v
}

import { useAuth } from '@/contexts/AuthContext'

export default function TransferPage(){
  const { t, i18n } = useTranslation()
  const [fromType, setFromType] = useState('bank')
  const [toType, setToType] = useState('cash')
  const [fromQuery, setFromQuery] = useState('')
  const [toQuery, setToQuery] = useState('')
  const dqFrom = useDebounce(fromQuery)
  const dqTo = useDebounce(toQuery)
  const [fromResults, setFromResults] = useState<any[]>([])
  const [toResults, setToResults] = useState<any[]>([])
  const [fromId, setFromId] = useState<string | null>(null)
  const [toId, setToId] = useState<string | null>(null)
  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState('USD')
  const [exchangeRate, setExchangeRate] = useState(1)
  const [date, setDate] = useState(new Date().toISOString().slice(0,10))
  const [reference, setReference] = useState('')
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [pendingTxn, setPendingTxn] = useState<any | null>(null)

  useEffect(()=>{ if (!dqFrom) return setFromResults([]); fetch(`/api/treasury/accounts?type=${fromType}`).then(r=>r.json()).then(d=> setFromResults((d||[]).filter((x:any)=> (x.name||x.bank_name||'').toLowerCase().includes(dqFrom.toLowerCase()))).catch(()=>{})) }, [dqFrom, fromType])
  useEffect(()=>{ if (!dqTo) return setToResults([]); fetch(`/api/treasury/accounts?type=${toType}`).then(r=>r.json()).then(d=> setToResults((d||[]).filter((x:any)=> (x.name||x.bank_name||'').toLowerCase().includes(dqTo.toLowerCase()))).catch(()=>{})) }, [dqTo, toType])

  const selectedFrom = useMemo(()=> fromResults.find(r=> r.id === fromId), [fromResults, fromId])
  const selectedTo = useMemo(()=> toResults.find(r=> r.id === toId), [toResults, toId])

  useEffect(()=>{
    if (selectedFrom && selectedFrom.currency !== currency){
      // fetch FX or prompt - simple: set exchangeRate to 1
      setExchangeRate(1)
    }
  }, [selectedFrom, currency])

  const previewBalance = () => {
    if (!selectedFrom) return null
    const bal = Number(selectedFrom.balance || 0) - Number(amount || 0)
    return bal
  }

  const { user } = useAuth()
  const canTransfer = user && (user.role === 'Admin' || String(user.role).toLowerCase().includes('treasury'))

  useEffect(()=>{
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        submit()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [amount, selectedFrom, selectedTo])

  const submit = async () => {
    if (!canTransfer) return toast.error(t('treasury.permission_denied') || 'Permission denied')
    if (!selectedFrom) return toast.error(t('treasury.from_account'))
    if (!selectedTo) return toast.error(t('treasury.to_account'))
    if (Number(amount) <= 0) return toast.error(t('treasury.amount'))
    // require typed confirmation for large amounts
    if (Number(amount) > 1000000) {
      const typed = prompt('Type CONFIRM to proceed')
      if (typed !== 'CONFIRM') return toast.error(t('treasury.confirm_required') || 'Confirmation required')
    }
    setConfirmOpen(false)
    const payload:any = { from_type: fromType, from_id: selectedFrom.id, to_type: toType, to_id: selectedTo.id, amount: Number(amount), currency, exchange_rate: exchangeRate, date, reference }
    // optimistic UI
    const temp = { id: 'temp-'+Date.now(), amount: Number(amount), date, reference, posted: false }
    setPendingTxn(temp)
    try{
      const res = await fetch('/api/treasury/transfer', { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-User-Id': user?.id || 'system', 'X-User-Roles': user?.role || '' }, body: JSON.stringify(payload) })
      if (!res.ok) throw new Error('failed')
      const data = await res.json()
      toast.success(t('success') || 'Done')
      setPendingTxn(null)
      // clear
      setAmount(''); setReference('')
    }catch(e){
      console.error(e)
      setPendingTxn(null)
      toast.error(t('error') || 'Error')
    }
  }

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('treasury.new_transfer')}</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('treasury.transfer')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm mb-1">{t('treasury.from_type')}</label>
              <select className="p-2 border rounded w-full" value={fromType} onChange={e=> setFromType(e.target.value)}>
                <option value="cash">{t('treasury.cash_accounts')}</option>
                <option value="bank">{t('treasury.bank_accounts')}</option>
              </select>
              <label className="block text-sm mb-1 mt-2">{t('treasury.from_account')}</label>
              <Input value={fromQuery} onChange={(e:any)=> { setFromQuery(e.target.value); setFromId(null) }} placeholder={t('treasury.from_account')} />
              {fromResults.length > 0 && fromQuery && (
                <div className="border rounded mt-1 max-h-40 overflow-auto bg-card">
                  {fromResults.map(r=> (
                    <div key={r.id} className="p-2 hover:bg-muted cursor-pointer" onClick={()=> { setFromId(r.id); setFromQuery(r.name || r.bank_name) }}>{r.name||r.bank_name} — {r.currency} — {Number(r.balance||0).toFixed(2)}</div>
                  ))}
                </div>
              )}

              {selectedFrom && <div className="mt-2 text-sm">{t('treasury.preview_balance')}: {previewBalance()}</div>}
            </div>

            <div>
              <label className="block text-sm mb-1">{t('treasury.to_type')}</label>
              <select className="p-2 border rounded w-full" value={toType} onChange={e=> setToType(e.target.value)}>
                <option value="cash">{t('treasury.cash_accounts')}</option>
                <option value="bank">{t('treasury.bank_accounts')}</option>
              </select>
              <label className="block text-sm mb-1 mt-2">{t('treasury.to_account')}</label>
              <Input value={toQuery} onChange={(e:any)=> { setToQuery(e.target.value); setToId(null) }} placeholder={t('treasury.to_account')} />
              {toResults.length > 0 && toQuery && (
                <div className="border rounded mt-1 max-h-40 overflow-auto bg-card">
                  {toResults.map(r=> (
                    <div key={r.id} className="p-2 hover:bg-muted cursor-pointer" onClick={()=> { setToId(r.id); setToQuery(r.name || r.bank_name) }}>{r.name||r.bank_name} — {r.currency} — {Number(r.balance||0).toFixed(2)}</div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div>
              <label className="block text-sm mb-1">{t('treasury.amount')}</label>
              <Input value={amount} onChange={(e:any)=> setAmount(e.target.value)} type="number" />
            </div>
            <div>
              <label className="block text-sm mb-1">Currency</label>
              <Input value={currency} onChange={(e:any)=> setCurrency(e.target.value)} />
            </div>
            <div>
              <label className="block text-sm mb-1">Exchange Rate</label>
              <Input value={exchangeRate} onChange={(e:any)=> setExchangeRate(Number(e.target.value))} type="number" />
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm mb-1">Date</label>
            <Input type="date" value={date} onChange={(e:any)=> setDate(e.target.value)} />
          </div>

          <div className="mt-4">
            <label className="block text-sm mb-1">Reference</label>
            <Input value={reference} onChange={(e:any)=> setReference(e.target.value)} />
          </div>

          <div className="flex gap-2 mt-4">
            <Button onClick={() => setConfirmOpen(true)}>{t('treasury.confirm_transfer')}</Button>
            <Button variant="outline" onClick={() => { setAmount(''); setReference('') }}>{t('treasury.reset')}</Button>
          </div>

          {pendingTxn && <div className="mt-4 p-3 border rounded bg-muted">Pending transaction: {pendingTxn.amount} — {pendingTxn.reference}</div>}

        </CardContent>
      </Card>

      <Modal open={confirmOpen} onOpenChange={setConfirmOpen} title={t('treasury.confirm_transfer')}>
        <div>
          <p>{t('treasury.are_you_sure_transfer')} {amount}?</p>
          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => setConfirmOpen(false)}>{t('cancel')}</Button>
            <Button onClick={submit}>{t('submit')}</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
