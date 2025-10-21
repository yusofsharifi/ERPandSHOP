import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import Modal from '@/components/ui/Modal'
import { useParams, useNavigate } from 'react-router-dom'

const InvoiceViewPage: React.FC = () => {
  const { id } = useParams()
  const [inv, setInv] = useState<any>(null)
  const [openPay, setOpenPay] = useState(false)
  const navigate = useNavigate()
  const fetchInv = async () => {
    const res = await fetch('/api/v1/arap/invoices')
    const list = await res.json()
    const found = list.find((i: any) => i.id === id)
    setInv(found)
  }
  useEffect(() => { fetchInv() }, [id])
  const post = async () => {
    await fetch(`/api/v1/arap/invoices/${id}/post`, { method: 'POST' })
    fetchInv()
  }
  const openPdf = () => {
    window.open(`/api/v1/arap/invoices/${id}/pdf`, '_blank')
  }
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Invoice</h2>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Invoice Details</CardTitle>
        </CardHeader>
        <CardContent>
          {!inv && <div>Loading...</div>}
          {inv && (
            <div>
              <div className="mb-2">Number: {inv.invoice_no}</div>
              <div className="mb-2">Date: {inv.date}</div>
              <div className="mb-2">Status: {inv.status}</div>
              <div className="mb-4">Total: {inv.total_amount} - Balance: {inv.balance_amount}</div>
              <h4 className="font-semibold mb-2">Lines</h4>
              <div className="space-y-2">
                {inv.lines.map((l: any) => (
                  <div key={l.id} className="p-2 border rounded">{l.description} — {l.line_total}</div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
        <CardFooter>
          <div className="flex gap-2 ml-auto">
            <Button onClick={() => setOpenPay(true)}>Register Payment</Button>
            <Button onClick={openPdf} variant="outline">Print</Button>
            <Button onClick={post}>Post</Button>
          </div>
        </CardFooter>
      </Card>

      <Modal open={openPay} onOpenChange={setOpenPay} title="Register Payment">
        <div className="space-y-3">
          <div>Simple payment form</div>
          <div className="flex justify-end">
            <Button variant="outline" onClick={() => setOpenPay(false)}>Cancel</Button>
            <Button onClick={() => { setOpenPay(false); navigate('/finance/payments') }} className="ml-2">Save</Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default InvoiceViewPage
