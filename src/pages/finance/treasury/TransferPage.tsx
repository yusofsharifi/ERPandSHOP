import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { useTranslation } from 'react-i18next'

const TransferPage: React.FC = () => {
  const { i18n, t } = useTranslation()
  const [sources, setSources] = useState<any[]>([])
  const [targets, setTargets] = useState<any[]>([])
  const [fromType, setFromType] = useState('bank')
  const [toType, setToType] = useState('cash')
  const [fromId, setFromId] = useState<string | null>(null)
  const [toId, setToId] = useState<string | null>(null)
  const [amount, setAmount] = useState<number>(0)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [previewBalance, setPreviewBalance] = useState<number | null>(null)

  useEffect(() => { fetchLists() }, [fromType, toType])

  const fetchLists = async () => {
    try {
      const s = await (await fetch(fromType === 'bank' ? '/api/v1/treasury/bank_accounts' : '/api/v1/treasury/cash_accounts')).json()
      const t = await (await fetch(toType === 'bank' ? '/api/v1/treasury/bank_accounts' : '/api/v1/treasury/cash_accounts')).json()
      setSources(s.items || s || [])
      setTargets(t.items || t || [])
    } catch (e) {}
  }

  useEffect(() => {
    const src = sources.find(s => s.id === fromId)
    if (src) {
      const bal = parseFloat(src.balance || 0) - amount
      setPreviewBalance(isNaN(bal) ? null : bal)
    } else setPreviewBalance(null)
  }, [fromId, amount, sources])

  const doTransfer = async () => {
    // call API
    await fetch('/api/v1/treasury/transfer', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ source_type: fromType, source_id: fromId, target_type: toType, target_id: toId, amount, date: new Date().toISOString().slice(0,10) }) })
    setConfirmOpen(false)
    // refresh
    fetchLists()
  }

  return (
    <div dir={i18n.language === 'fa' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('treasury.transfer') || 'Transfer'}</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>{t('treasury.new_transfer') || 'New Transfer'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm mb-1">{t('treasury.from_type') || 'From Type'}</label>
              <select value={fromType} onChange={(e)=> setFromType(e.target.value)} className="w-full p-2 border rounded">
                <option value="bank">Bank</option>
                <option value="cash">Cash</option>
              </select>
              <label className="block text-sm mb-1 mt-2">{t('treasury.from_account') || 'From Account'}</label>
              <select value={fromId || ''} onChange={(e)=> setFromId(e.target.value || null)} className="w-full p-2 border rounded">
                <option value="">-- select --</option>
                {sources.map(s => <option key={s.id} value={s.id}>{s.bank_name || s.name} ({s.balance})</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm mb-1">{t('treasury.to_type') || 'To Type'}</label>
              <select value={toType} onChange={(e)=> setToType(e.target.value)} className="w-full p-2 border rounded">
                <option value="cash">Cash</option>
                <option value="bank">Bank</option>
              </select>
              <label className="block text-sm mb-1 mt-2">{t('treasury.to_account') || 'To Account'}</label>
              <select value={toId || ''} onChange={(e)=> setToId(e.target.value || null)} className="w-full p-2 border rounded">
                <option value="">-- select --</option>
                {targets.map(s => <option key={s.id} value={s.id}>{s.bank_name || s.name} ({s.balance})</option>)}
              </select>
            </div>
          </div>

          <div className="mt-4">
            <label className="block text-sm mb-1">{t('treasury.amount') || 'Amount'}</label>
            <Input type="number" value={amount} onChange={(e)=> setAmount(Number(e.target.value))} />
          </div>

          <div className="mt-4">
            <div className="text-sm">{t('Preview balance after transfer') || 'Preview balance after transfer'}: {previewBalance !== null ? previewBalance.toFixed(2) : '-'}</div>
          </div>

          <div className="flex justify-end gap-2 mt-4">
            <Button variant="outline" onClick={() => { setFromId(null); setToId(null); setAmount(0) }}>{t('Reset') || 'Reset'}</Button>
            <Button onClick={() => setConfirmOpen(true)}>{t('treasury.transfer') || 'Transfer'}</Button>
          </div>
        </CardContent>
      </Card>

      <Modal open={confirmOpen} onOpenChange={setConfirmOpen} title={t('Confirm Transfer') || 'Confirm Transfer'}>
        <div className="space-y-3">
          <div>{t('Are you sure you want to transfer') || 'Are you sure you want to transfer'} <strong>{amount}</strong></div>
          <div className="flex justify-end">
            <Button variant="outline" onClick={() => setConfirmOpen(false)}>{t('Cancel') || 'Cancel'}</Button>
            <Button onClick={doTransfer} className="ml-2">{t('Confirm') || 'Confirm'}</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default TransferPage
