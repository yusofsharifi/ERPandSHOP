import React from 'react'

const InvoiceSummary: React.FC<{ subtotal:number, tax:number, discount:number, net:number }> = ({ subtotal, tax, discount, net }) => {
  return (
    <div className="border p-4 rounded">
      <div className="flex justify-between"><div>جمع فرعی</div><div>{subtotal.toFixed(2)}</div></div>
      <div className="flex justify-between"><div>مالیات</div><div>{tax.toFixed(2)}</div></div>
      <div className="flex justify-between"><div>تخفیف</div><div>-{discount.toFixed(2)}</div></div>
      <hr className="my-2" />
      <div className="flex justify-between font-bold"><div>جمع کل</div><div>{net.toFixed(2)}</div></div>
    </div>
  )
}

export default InvoiceSummary
