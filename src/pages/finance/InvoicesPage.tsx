import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import { Link } from 'react-router-dom'

interface Invoice { id: string; invoice_no: string; date: string; total_amount: string; balance_amount: string; status: string; invoice_type: string }

const InvoicesPage: React.FC = () => {
  const [items, setItems] = useState<Invoice[]>([])
  const [type, setType] = useState<string | undefined>(undefined)
  const [status, setStatus] = useState<string | undefined>(undefined)
  const fetchList = async () => {
    const params = new URLSearchParams()
    if (type) params.set('type', type)
    if (status) params.set('status', status)
    const res = await fetch('/api/v1/arap/invoices?' + params.toString())
    const data = await res.json()
    setItems(data)
  }
  useEffect(() => { fetchList() }, [type, status])
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Invoices</h2>
        <div className="flex items-center gap-2">
          <Link to="/finance/invoices/new"><Button>New Invoice</Button></Link>
        </div>
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Invoice list</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <select value={type || ''} onChange={(e)=> setType(e.target.value || undefined)} className="p-2 border rounded">
              <option value="">All types</option>
              <option value="sale">Sale</option>
              <option value="purchase">Purchase</option>
            </select>
            <select value={status || ''} onChange={(e)=> setStatus(e.target.value || undefined)} className="p-2 border rounded">
              <option value="">All status</option>
              <option value="draft">Draft</option>
              <option value="open">Open</option>
              <option value="partial">Partial</option>
              <option value="paid">Paid</option>
            </select>
            <Button variant="outline" onClick={fetchList}>Refresh</Button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left">
                  <th className="px-2 py-1">#</th>
                  <th className="px-2 py-1">Date</th>
                  <th className="px-2 py-1">Type</th>
                  <th className="px-2 py-1">Total</th>
                  <th className="px-2 py-1">Balance</th>
                  <th className="px-2 py-1">Status</th>
                  <th className="px-2 py-1">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map(inv => (
                  <tr key={inv.id} className="border-t">
                    <td className="px-2 py-2">{inv.invoice_no}</td>
                    <td className="px-2 py-2">{inv.date}</td>
                    <td className="px-2 py-2">{inv.invoice_type}</td>
                    <td className="px-2 py-2">{inv.total_amount}</td>
                    <td className="px-2 py-2">{inv.balance_amount}</td>
                    <td className="px-2 py-2">{inv.status}</td>
                    <td className="px-2 py-2">
                      <Link to={`/finance/invoices/${inv.id}`} className="text-primary underline">View</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default InvoicesPage
