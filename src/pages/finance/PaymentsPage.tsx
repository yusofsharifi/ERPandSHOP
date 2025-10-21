import React, { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'

interface Payment { id: number; amount: string; method: string; payment_date: string; partner_id: string }

const PaymentsPage: React.FC = () => {
  const [items, setItems] = useState<Payment[]>([])
  const fetchList = async () => {
    const res = await fetch('/api/v1/arap/payments')
    if (!res.ok) return setItems([])
    const data = await res.json()
    setItems(data)
  }
  useEffect(() => { fetchList() }, [])
  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">Payments</h2>
        <div />
      </div>
      <Card>
        <CardHeader>
          <CardTitle>Payments</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full table-auto">
              <thead>
                <tr className="text-left">
                  <th className="px-2 py-1">Date</th>
                  <th className="px-2 py-1">Partner</th>
                  <th className="px-2 py-1">Amount</th>
                  <th className="px-2 py-1">Method</th>
                </tr>
              </thead>
              <tbody>
                {items.map(p => (
                  <tr key={p.id} className="border-t">
                    <td className="px-2 py-2">{p.payment_date}</td>
                    <td className="px-2 py-2">{p.partner_id}</td>
                    <td className="px-2 py-2">{p.amount}</td>
                    <td className="px-2 py-2">{p.method}</td>
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

export default PaymentsPage
