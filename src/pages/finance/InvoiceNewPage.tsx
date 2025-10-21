import React, { useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import { Input } from '@/components/ui/Input'
import { useNavigate } from 'react-router-dom'

interface Line { id: string; description: string; qty: number; unit_price: number; tax_rate: number; line_total: number }

const InvoiceNewPage: React.FC = () => {
  const [step, setStep] = useState(0)
  const [partnerId, setPartnerId] = useState('')
  const [type, setType] = useState('sale')
  const [lines, setLines] = useState<Line[]>([])
  const [openPayment, setOpenPayment] = useState(false)
  const navigate = useNavigate()

  const addLine = () => {
    setLines([...lines, { id: Date.now().toString(), description: '', qty: 1, unit_price: 0, tax_rate: 0, line_total: 0 }])
  }
  const updateLine = (id: string, patch: Partial<Line>) => {
    setLines(lines.map(l => l.id === id ? { ...l, ...patch, line_total: ((patch.qty ?? l.qty) * (patch.unit_price ?? l.unit_price)) * (1 + (patch.tax_rate ?? l.tax_rate)) } : l))
  }
  const totals = lines.reduce((acc, l) => acc + (l.line_total || 0), 0)

  const create = async () => {
    const payload = { partner_id: partnerId, invoice_type: type, date: new Date().toISOString().slice(0,10), lines: lines.map(l => ({ product_id: null, description: l.description, qty: l.qty, unit_price: l.unit_price, tax_rate: l.tax_rate })) }
    const res = await fetch('/api/v1/arap/invoices', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(payload) })
    if (res.ok) {
      const inv = await res.json()
      navigate(`/finance/invoices/${inv.id}`)
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">New Invoice</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Invoice Wizard</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4">Step {step+1} / 3</div>
          {step === 0 && (
            <div className="space-y-3">
              <div>
                <label className="block text-sm mb-1">Partner ID</label>
                <Input value={partnerId} onChange={(e)=> setPartnerId(e.target.value)} placeholder="partner id" />
              </div>
              <div>
                <label className="block text-sm mb-1">Type</label>
                <select value={type} onChange={(e)=> setType(e.target.value)} className="p-2 border rounded">
                  <option value="sale">Sale</option>
                  <option value="purchase">Purchase</option>
                </select>
              </div>
            </div>
          )}
          {step === 1 && (
            <div>
              <div className="mb-2 flex justify-between">
                <h4 className="font-semibold">Lines</h4>
                <Button onClick={addLine}>Add Line</Button>
              </div>
              <div className="space-y-2">
                {lines.map(l => (
                  <div key={l.id} className="p-2 border rounded flex gap-2">
                    <Input placeholder="Description" value={l.description} onChange={(e)=> updateLine(l.id, { description: e.target.value })} />
                    <Input type="number" value={l.qty} onChange={(e)=> updateLine(l.id, { qty: Number(e.target.value) })} className="w-24" />
                    <Input type="number" value={l.unit_price} onChange={(e)=> updateLine(l.id, { unit_price: Number(e.target.value) })} className="w-28" />
                    <Input type="number" value={l.tax_rate} onChange={(e)=> updateLine(l.id, { tax_rate: Number(e.target.value) })} className="w-24" />
                    <div className="w-32">{l.line_total.toFixed(2)}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
          {step === 2 && (
            <div>
              <h4 className="font-semibold mb-2">Totals</h4>
              <div className="mb-2">Subtotal: {totals.toFixed(2)}</div>
              <div className="mb-2">Total: {totals.toFixed(2)}</div>
            </div>
          )}

          <div className="flex justify-end gap-2 mt-4">
            {step > 0 && <Button variant="outline" onClick={() => setStep(s => s-1)}>Back</Button>}
            {step < 2 ? <Button onClick={() => setStep(s => s+1)}>Next</Button> : <Button onClick={create}>Create</Button>}
          </div>
        </CardContent>
      </Card>

      <Modal open={openPayment} onOpenChange={setOpenPayment} title="Register Payment">
        <div>Payment form</div>
      </Modal>
    </div>
  )
}

export default InvoiceNewPage
