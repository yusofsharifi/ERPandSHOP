import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Button } from '@/components/ui/Button'
import StatusBadge from '@/components/sales/StatusBadge'
import DeliverySection from '@/components/sales/DeliverySection'
import InvoiceButton from '@/components/sales/InvoiceButton'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'

const OrderDetail: React.FC = () => {
  const { id } = useParams()
  const { i18n } = useTranslation()
  const [order, setOrder] = useState<any | null>(null)
  const [tab, setTab] = useState('overview')

  const fetchOrder = async () => {
    if (!id) return
    try {
      const res = await fetch(`/api/v1/sales-orders/${id}`)
      if (!res.ok) { toast.error('Error'); return }
      const json = await res.json()
      setOrder(json)
    } catch (e) { toast.error('Error') }
  }

  useEffect(()=> { fetchOrder() }, [id])

  if (!order) return <div>{i18n.language === 'fa' ? 'در حال بارگذاری...' : 'Loading...'}</div>

  return (
    <div className={i18n.language === 'fa' ? 'font-farsi' : ''}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-semibold">{i18n.language === 'fa' ? 'جزئیات سفارش' : 'Order Detail'}</h2>
        <div className="flex gap-2 items-center">
          <StatusBadge status={order.status} />
          <InvoiceButton orderId={order.id} onInvoiced={()=> fetchOrder()} />
        </div>
      </div>

      <div className="mb-4">
        <nav className="flex gap-2">
          <button onClick={()=> setTab('overview')} className={`px-3 py-1 ${tab==='overview' ? 'bg-gray-100' : ''}`}>{i18n.language === 'fa' ? 'نمای کلی' : 'Overview'}</button>
          <button onClick={()=> setTab('delivery')} className={`px-3 py-1 ${tab==='delivery' ? 'bg-gray-100' : ''}`}>{i18n.language === 'fa' ? 'ارسال' : 'Delivery'}</button>
          <button onClick={()=> setTab('invoice')} className={`px-3 py-1 ${tab==='invoice' ? 'bg-gray-100' : ''}`}>{i18n.language === 'fa' ? 'فاکتور' : 'Invoice'}</button>
          <button onClick={()=> setTab('history')} className={`px-3 py-1 ${tab==='history' ? 'bg-gray-100' : ''}`}>{i18n.language === 'fa' ? 'تاریخچه' : 'History'}</button>
        </nav>
      </div>

      {tab === 'overview' && (
        <Card>
          <CardHeader><CardTitle>{i18n.language === 'fa' ? 'مشخصات سفارش' : 'Overview'}</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div><strong>{i18n.language === 'fa' ? 'شماره سفارش' : 'Order No'}:</strong> {order.order_no}</div>
                <div><strong>{i18n.language === 'fa' ? 'مشتری' : 'Customer'}:</strong> {order.customer_id}</div>
                <div><strong>{i18n.language === 'fa' ? 'تاریخ' : 'Date'}:</strong> {order.date}</div>
              </div>
              <div>
                <div><strong>{i18n.language === 'fa' ? 'جمع کل' : 'Total'}:</strong> {order.net_amount}</div>
                <div><strong>{i18n.language === 'fa' ? 'وضعیت' : 'Status'}:</strong> <StatusBadge status={order.status} /></div>
              </div>
            </div>

            <div className="mt-4">
              <h4 className="font-medium mb-2">{i18n.language === 'fa' ? 'ردیف‌ها' : 'Lines'}</h4>
              <div className="space-y-2">
                {order.lines && order.lines.map((l:any)=>(
                  <div key={l.id} className="p-2 border rounded">
                    <div className="flex justify-between"><div>{l.description}</div><div>{l.line_total}</div></div>
                    <div className="text-sm text-muted-foreground">{l.quantity} x {l.unit_price} (tax {l.tax_rate}%)</div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {tab === 'delivery' && (
        <DeliverySection orderId={id!} initial={{}} onUpdated={()=> fetchOrder()} />
      )}

      {tab === 'invoice' && (
        <Card><CardHeader><CardTitle>{i18n.language === 'fa' ? 'فاکتور مرتبط' : 'Linked Invoice'}</CardTitle></CardHeader><CardContent>{order.invoice_id ? <div>{order.invoice_id}</div> : <div>{i18n.language === 'fa' ? 'هنوز تولید نشده' : 'Not generated'}</div>}</CardContent></Card>
      )}

      {tab === 'history' && (
        <Card><CardHeader><CardTitle>{i18n.language === 'fa' ? 'تاریخچه' : 'History'}</CardTitle></CardHeader><CardContent><div>{i18n.language === 'fa' ? 'رویدادها نمایش داده می‌شود' : 'Audit events will be shown'}</div></CardContent></Card>
      )}
    </div>
  )
}

export default OrderDetail
