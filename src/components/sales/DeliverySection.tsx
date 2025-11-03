import React, { useState } from 'react'
import { Input } from '@/components/ui/Input'
import { Button } from '@/components/ui/Button'
import toast from 'react-hot-toast'
import { useTranslation } from 'react-i18next'

const DeliverySection: React.FC<{ orderId:string, initial?:any, onUpdated?:()=>void }> = ({ orderId, initial, onUpdated }) => {
  const { i18n } = useTranslation()
  const [carrier, setCarrier] = useState(initial?.carrier || '')
  const [tracking, setTracking] = useState(initial?.tracking_code || '')
  const [status, setStatus] = useState(initial?.status || 'pending')

  const save = async () => {
    try {
      // placeholder: update via sales-orders ship endpoint
      const res = await fetch(`/api/v1/sales-orders/${orderId}/ship`, { method: 'POST', headers: {'Content-Type':'application/json','X-User-Id':'1','X-User-Roles':'Sales'}, body: JSON.stringify({ carrier, tracking_code: tracking }) })
      if (!res.ok) { toast.error('Error'); return }
      toast.success(i18n.language==='fa' ? 'اطلاعات ارسال ذخیره شد' : 'Delivery updated')
      onUpdated && onUpdated()
    } catch (e) { toast.error('Error') }
  }

  return (
    <div className="border p-4 rounded">
      <div className="mb-2"><label className="block text-sm">{i18n.language==='fa' ? 'حمل‌کننده' : 'Carrier'}</label><Input value={carrier} onChange={(e:any)=> setCarrier(e.target.value)} /></div>
      <div className="mb-2"><label className="block text-sm">{i18n.language==='fa' ? 'کد رهگیری' : 'Tracking code'}</label><Input value={tracking} onChange={(e:any)=> setTracking(e.target.value)} /></div>
      <div className="mb-2"><label className="block text-sm">{i18n.language==='fa' ? 'وضعیت ارسال' : 'Status'}</label>
        <select value={status} onChange={(e)=> setStatus(e.target.value)} className="p-2 border rounded w-full">
          <option value="pending">{i18n.language==='fa' ? 'در انتظار' : 'Pending'}</option>
          <option value="in_transit">{i18n.language==='fa' ? 'در مسیر' : 'In transit'}</option>
          <option value="delivered">{i18n.language==='fa' ? 'تحویل شده' : 'Delivered'}</option>
        </select>
      </div>
      <div className="flex justify-end gap-2 mt-2"><Button variant="outline" onClick={save}>{i18n.language==='fa' ? 'به‌روزرسانی' : 'Update'}</Button></div>
    </div>
  )
}

export default DeliverySection
