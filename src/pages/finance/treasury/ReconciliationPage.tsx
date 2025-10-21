import React, { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { useTranslation } from 'react-i18next'

const ReconciliationPage: React.FC = () => {
  const { i18n, t } = useTranslation()
  const [fileName, setFileName] = useState<string | null>(null)
  const [mappings, setMappings] = useState<{[k:string]:string}>({ date: 'date', desc: 'description', amount: 'amount' })
  const [previewRows, setPreviewRows] = useState<any[]>([])
  const [matches, setMatches] = useState<any[]>([])

  const onFile = async (f?: File) => {
    if (!f) return
    setFileName(f.name)
    const text = await f.text()
    // naive CSV parse first 5 lines
    const lines = text.split('\n').slice(0,5)
    const cols = lines[0].split(',')
    setPreviewRows(lines.map(l=> l.split(',')))
  }

  const suggestMatches = async () => {
    // mock suggestions
    setMatches([
      { stmt: 'TXN123', amount: '100.00', suggested: 'Match to payment 1' },
      { stmt: 'TXN124', amount: '50.00', suggested: 'Match to payment 2' }
    ])
  }

  const applyReconciliation = async () => {
    // call API to apply matches
    alert('Applied')
  }

  return (
    <div dir={i18n.language === 'fa' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{t('treasury.upload_statement') || 'Bank Reconciliation'}</h2>
        <div />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>{t('Upload Statement') || 'Upload Statement'}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">
            <input type="file" accept=".csv" onChange={(e)=> onFile(e.target.files?.[0])} />
            {fileName && <div className="text-sm mt-2">{t('Selected') || 'Selected'}: {fileName}</div>}
          </div>

          <div className="mb-4">
            <h4 className="font-semibold mb-2">{t('Field mapping') || 'Field mapping'}</h4>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              <div>
                <label className="block text-sm mb-1">{t('Date field') || 'Date field'}</label>
                <input value={mappings.date} onChange={(e)=> setMappings({...mappings, date: e.target.value})} className="p-2 border rounded w-full" />
              </div>
              <div>
                <label className="block text-sm mb-1">{t('Description field') || 'Description field'}</label>
                <input value={mappings.desc} onChange={(e)=> setMappings({...mappings, desc: e.target.value})} className="p-2 border rounded w-full" />
              </div>
              <div>
                <label className="block text-sm mb-1">{t('Amount field') || 'Amount field'}</label>
                <input value={mappings.amount} onChange={(e)=> setMappings({...mappings, amount: e.target.value})} className="p-2 border rounded w-full" />
              </div>
            </div>
          </div>

          <div className="mb-4">
            <Button onClick={suggestMatches}>{t('Suggest matches') || 'Suggest matches'}</Button>
          </div>

          <div>
            <h4 className="font-semibold mb-2">{t('Matches') || 'Matches'}</h4>
            <div className="space-y-2">
              {matches.map((m, idx) => (
                <div key={idx} className="p-2 border rounded flex justify-between">
                  <div>{m.stmt} — {m.amount}</div>
                  <div className="text-sm text-muted-foreground">{m.suggested}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-end mt-4">
            <Button variant="outline" onClick={()=> setPreviewRows([])}>{t('Reset') || 'Reset'}</Button>
            <Button onClick={applyReconciliation} className="ml-2">{t('Apply') || 'Apply'}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ReconciliationPage
