import React from 'react'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'

const InvoiceButton: React.FC<{ orderId:string, onInvoiced?: (res:any)=>void }> = ({ orderId, onInvoiced }) => {
  const doInvoice = async () => {
    try {
      const res = await fetch(`/api/v1/sales-orders/${orderId}/invoice`, { method: 'POST', headers: {'X-User-Id':'1','X-User-Roles':'Sales'} })
      if (!res.ok) { const err = await res.json().catch(()=>({})); toast.error(err?.detail?.message?.en || 'Error'); return }
      const data = await res.json()
      toast.success('Invoice generated')
      onInvoiced && onInvoiced(data)
    } catch (e) { toast.error('Error') }
  }
  return <Button onClick={doInvoice}>تولید فاکتور</Button>
}

export default InvoiceButton
